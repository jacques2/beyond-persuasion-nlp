"""Explicit ethical rules used by the protection layer.

This module is intentionally simple and deterministic. It contains:

- the emotions considered ethically sensitive,
- the default thresholds used by the project,
- helper functions that turn emotion predictions into rule signals.

The goal is to keep the ethical policy easy to inspect
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set

from beyond_persuasion.schemas import EmotionPrediction


DEFAULT_VULNERABLE_EMOTIONS = {"sadness", "anger", "fear", "stress"}

# These weights let the project express that some emotions may count as
# slightly more critical than others in the vulnerability estimate.
DEFAULT_EMOTION_WEIGHTS = {
    "sadness": 1.00,
    "fear": 0.95,
    "stress": 0.90,
    "anger": 0.85,
    "neutral": 0.00,
}


@dataclass
class EthicalRulesConfig:
    """Configuration for the rule-based ethical policy."""

    vulnerable_emotions: Set[str] = field(
        default_factory=lambda: set(DEFAULT_VULNERABLE_EMOTIONS)
    )
    emotion_weights: Dict[str, float] = field(
        default_factory=lambda: dict(DEFAULT_EMOTION_WEIGHTS)
    )

    # If the dominant vulnerable emotion is strong enough, protection is
    # activated even without additional evidence.
    primary_emotion_threshold: float = 0.60

    # If multiple negative emotions accumulate, protection can also be
    # activated through the combined score.
    combined_emotion_threshold: float = 0.70

    # This extra threshold keeps the system from overreacting to weak signals.
    minimum_confidence_for_flag: float = 0.55

    def __post_init__(self) -> None:
        for field_name in (
            "primary_emotion_threshold",
            "combined_emotion_threshold",
            "minimum_confidence_for_flag",
        ):
            value = getattr(self, field_name)
            if not 0.0 <= value <= 1.0:
                raise ValueError("%s must be between 0 and 1" % field_name)


def is_vulnerable_emotion(label: str, config: EthicalRulesConfig) -> bool:
    """Return True when the label belongs to the project's vulnerable set."""
    return label.lower() in config.vulnerable_emotions


def combined_negative_score(
    prediction: EmotionPrediction,
    config: EthicalRulesConfig,
) -> float:
    """Sum the scores of all vulnerable emotions.

    Because the prediction scores are already normalized, the returned value
    also stays between 0 and 1.
    """
    score = 0.0

    for emotion in config.vulnerable_emotions:
        score += prediction.score_for(emotion)

    return _clamp(score)


def weighted_risk_score(
    prediction: EmotionPrediction,
    config: EthicalRulesConfig,
) -> float:
    """Compute a single risk score from the emotion distribution.

    The weighted score is useful because it combines:
    - the full distribution, not only the top label;
    - the ethical importance assigned to each vulnerable emotion.
    """
    risk_score = 0.0

    for emotion, weight in config.emotion_weights.items():
        risk_score += prediction.score_for(emotion) * weight

    return _clamp(risk_score)


def primary_emotion_rule_triggered(
    prediction: EmotionPrediction,
    config: EthicalRulesConfig,
) -> bool:
    """Return True when the top emotion is vulnerable and strong enough."""
    if not is_vulnerable_emotion(prediction.label, config):
        return False

    primary_score = prediction.score_for(prediction.label)

    return (
        prediction.confidence >= config.minimum_confidence_for_flag
        and primary_score >= config.primary_emotion_threshold
    )


def combined_emotions_rule_triggered(
    prediction: EmotionPrediction,
    config: EthicalRulesConfig,
) -> bool:
    """Return True when negative emotions are strong in aggregate."""
    return combined_negative_score(prediction, config) >= config.combined_emotion_threshold


def get_triggered_rules(
    prediction: EmotionPrediction,
    config: EthicalRulesConfig,
) -> List[str]:
    """Return the list of rule identifiers activated by this prediction."""
    triggered_rules = []

    if primary_emotion_rule_triggered(prediction, config):
        triggered_rules.append("primary_emotion_threshold")

    if combined_emotions_rule_triggered(prediction, config):
        triggered_rules.append("combined_negative_emotions")

    return triggered_rules


def build_rationale(
    prediction: EmotionPrediction,
    config: EthicalRulesConfig,
    triggered_rules: List[str],
) -> str:
    """Build a short explanation for logging and reporting."""
    if not triggered_rules:
        return (
            "No protection rule was triggered. "
            "The detected emotional signal stayed below the configured thresholds."
        )

    rationale_parts = [
        "Detected dominant emotion '%s' with confidence %.2f."
        % (prediction.label, prediction.confidence)
    ]

    if "primary_emotion_threshold" in triggered_rules:
        rationale_parts.append(
            "The dominant vulnerable emotion exceeded the primary threshold."
        )

    if "combined_negative_emotions" in triggered_rules:
        rationale_parts.append(
            "The combined negative emotion score exceeded the aggregate threshold."
        )

    return " ".join(rationale_parts)


def _clamp(value: float) -> float:
    """Keep numeric scores inside the 0-1 range."""
    return max(0.0, min(1.0, value))
