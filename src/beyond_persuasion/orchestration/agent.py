"""End-to-end coordinator for the conversational agent."""

from beyond_persuasion.affective.pipeline import EmotionAnalyzer
from beyond_persuasion.ethics.engine import EthicalEngine
from beyond_persuasion.llm.local_model import LocalLLMClient
from beyond_persuasion.llm.prompting import build_system_prompt, build_user_prompt
from beyond_persuasion.schemas import ConversationTurn


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

    def respond(self, turn: ConversationTurn) -> str:
        """Run the full guarded conversation pipeline."""
        prediction = self.emotion_analyzer.predict(turn.user_text)
        assessment = self.ethical_engine.assess(prediction)
        system_prompt = build_system_prompt(assessment)
        user_prompt = build_user_prompt(turn)
        return self.llm_client.generate(system_prompt=system_prompt, user_prompt=user_prompt)
