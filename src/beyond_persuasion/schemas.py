"""Shared dataclasses and protocol-like interfaces used across modules."""

from dataclasses import dataclass, field


@dataclass
class EmotionPrediction:
    """Output of the affective computing module."""

    label: str
    confidence: float
    scores: dict[str, float] = field(default_factory=dict)


@dataclass
class EthicalAssessment:
    """Decision produced by the ethical engine."""

    is_vulnerable: bool
    risk_score: float
    rationale: str


@dataclass
class ConversationTurn:
    """Minimal conversation unit passed through the pipeline."""

    user_text: str
    metadata: dict[str, str] = field(default_factory=dict)
