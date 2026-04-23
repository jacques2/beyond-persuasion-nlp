"""End-to-end coordinator for the conversational agent."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from beyond_persuasion.affective.pipeline import EmotionAnalyzer
from beyond_persuasion.affective.pipeline import EmotionAnalyzerConfig
from beyond_persuasion.config import load_yaml_config
from beyond_persuasion.ethics.engine import EthicalEngine
from beyond_persuasion.ethics.rules import EthicalRulesConfig
from beyond_persuasion.llm.local_model import LocalLLMClient
from beyond_persuasion.llm.local_model import LocalLLMConfig
from beyond_persuasion.llm.prompting import build_system_prompt, build_user_prompt
from beyond_persuasion.schemas import ConversationTurn, EmotionPrediction, EthicalAssessment


@dataclass
class AgentRunResult:
    """Collect all intermediate outputs for one conversation turn."""

    turn: ConversationTurn
    prediction: EmotionPrediction
    assessment: EthicalAssessment
    system_prompt: str
    user_prompt: str
    response_text: str


class SafeConversationAgent:
    """Compose affective analysis, ethical rules, and local generation."""

    def __init__(
        self,
        emotion_analyzer: EmotionAnalyzer,
        ethical_engine: EthicalEngine,
        llm_client: LocalLLMClient,
    ) -> None:
        self.emotion_analyzer = emotion_analyzer
        self.ethical_engine = ethical_engine
        self.llm_client = llm_client

    @classmethod
    # I take the config from the YAML file and build the three main components of the agent.
    def from_config(cls, config: Dict[str, Any]) -> "SafeConversationAgent":
        """Build the full agent stack from a plain configuration dictionary."""
        affective_config = config.get("affective", {})
        ethics_config = config.get("ethics", {})
        llm_config = config.get("llm", {})

        emotion_analyzer = EmotionAnalyzer(
            EmotionAnalyzerConfig(
                # I use normalize_optional_string to allow for empty placeholders in the YAML config that get treated as None.
                model_name=_normalize_optional_string(affective_config.get("model_name")),
                use_transformers=bool(affective_config.get("use_transformers", True)),
            )
        )

        ethical_engine = EthicalEngine(
            EthicalRulesConfig(
                primary_emotion_threshold=float(
                    ethics_config.get("primary_emotion_threshold", 0.60)
                ),
                combined_emotion_threshold=float(
                    ethics_config.get("combined_emotion_threshold", 0.70)
                ),
                minimum_confidence_for_flag=float(
                    ethics_config.get("minimum_confidence_for_flag", 0.55)
                ),
            )
        )

        llm_client = LocalLLMClient(
            LocalLLMConfig(
                backend=str(llm_config.get("backend", "mock")),
                model_path=_normalize_optional_string(llm_config.get("model_path")),
                chat_format=_normalize_optional_string(llm_config.get("chat_format")),
                max_tokens=int(llm_config.get("max_tokens", 256)),
                temperature=float(llm_config.get("temperature", 0.3)),
                n_ctx=int(llm_config.get("n_ctx", 2048)),
                n_gpu_layers=int(llm_config.get("n_gpu_layers", -1)),
            )
        )

        return cls(
            emotion_analyzer=emotion_analyzer,
            ethical_engine=ethical_engine,
            llm_client=llm_client,
        )

    @classmethod
    def from_config_file(cls, path: Optional[Path] = None) -> "SafeConversationAgent":
        """Build the agent stack from the project's YAML configuration file."""
        return cls.from_config(load_yaml_config(path))

    def respond(self, turn: ConversationTurn) -> str:
        """Run the full guarded conversation pipeline and return only the text."""
        return self.run(turn).response_text

    def run(self, turn: ConversationTurn) -> AgentRunResult:
        """Run the full guarded conversation pipeline with full intermediate outputs."""
        # First we get the emotional prediction from the user's input text
        prediction = self.emotion_analyzer.predict(turn.user_text)

        # Second, we assess the ethical risk based on the emotional prediction
        assessment = self.ethical_engine.assess(prediction)

        # Finally, we build the prompts and get the LLM response. The system prompt includes the ethical assessment to guide the model's response.
        system_prompt = build_system_prompt(assessment)
        user_prompt = build_user_prompt(turn)
        response_text = self.llm_client.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        return AgentRunResult(
            turn=turn,
            prediction=prediction,
            assessment=assessment,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_text=response_text,
        )


def _normalize_optional_string(value: Any) -> Optional[str]:
    """Convert empty placeholder-like values into None."""
    if value is None:
        return None

    text = str(value).strip()
    if not text or text.lower() in ("none", "null", "todo", "todo/local-model-path", "todo/emotion-model"):
        return None

    return text
