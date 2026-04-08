"""Shared data structures used across the project.

These classes are intentionally simple because they are the "glue"
between the main modules of the repository:

- the affective module produces an ``EmotionPrediction``
- the ethical module converts it into an ``EthicalAssessment``
- the orchestration layer moves a ``ConversationTurn`` through the pipeline
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ConversationTurn:
    """Represent one user input handled by the system.
    This is the first object that enters the pipeline
    """

    user_text: str
    conversation_id: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None: # check if user_text is not empty or made of whitespaces
        # Keep the input clean early so downstream modules receive a
        # predictable value.
        self.user_text = self.user_text.strip()

        if not self.user_text:
            raise ValueError("user_text cannot be empty")


@dataclass
class EmotionPrediction:
    """Store the output of the emotion detection step.

    Attributes:
        label:
            The main emotion selected by the model or heuristic.
        confidence:
            Confidence assigned to the selected label. We keep it between
            0 and 1 to make thresholds easy to reason about.
        scores:
            Optional distribution over emotions, for example:
            {"sadness": 0.82, "neutral": 0.10, "anger": 0.08}
    """

    label: str
    confidence: float
    scores: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Normalize the label so rules do not have to handle many variants.
        self.label = self.label.strip().lower()

        if not self.label:
            raise ValueError("label cannot be empty")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")

        for emotion, score in self.scores.items():
            if not 0.0 <= score <= 1.0:
                raise ValueError(
                    f"score for emotion '{emotion}' must be between 0 and 1"
                )

    def score_for(self, emotion: str) -> float:
        """Return the score for one emotion, or 0 if it is missing."""
        return self.scores.get(emotion.lower(), 0.0)


@dataclass
class EthicalAssessment:
    """Store the decision produced by the ethical engine.

    Attributes:
        is_vulnerable:
            True when the user should be considered emotionally vulnerable.
        risk_score:
            A numeric summary of the detected risk, also between 0 and 1.
        rationale:
            A short explanation that can be logged and reused in the report.
        triggered_rules:
            Names of the rules that caused the protection flag to activate.
    """

    is_vulnerable: bool
    risk_score: float
    rationale: str
    triggered_rules: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not 0.0 <= self.risk_score <= 1.0:
            raise ValueError("risk_score must be between 0 and 1")

        self.rationale = self.rationale.strip()

        if not self.rationale:
            raise ValueError("rationale cannot be empty")

    @property
    def protection_enabled(self) -> bool:
        """Expose a clear name for the behavior switch used by the LLM layer."""
        return self.is_vulnerable
