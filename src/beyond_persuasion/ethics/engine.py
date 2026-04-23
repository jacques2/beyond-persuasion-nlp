"""Rule-based ethical engine.

This module should stay interpretable and easy to audit.
Avoid mixing policy decisions with model inference details.
"""

from typing import Optional

from beyond_persuasion.ethics.rules import (
    EthicalRulesConfig,
    build_rationale,
    combined_negative_score,
    get_triggered_rules,
    weighted_risk_score,
)
from beyond_persuasion.schemas import EmotionPrediction, EthicalAssessment


class EthicalEngine:
    """Apply vulnerability rules to affective predictions."""

    def __init__(self, config: Optional[EthicalRulesConfig] = None) -> None:
        self.config = config or EthicalRulesConfig()

    def assess(self, prediction: EmotionPrediction) -> EthicalAssessment:
        """Convert emotional evidence into an ethical risk decision.

        The engine keeps the decision logic intentionally explicit:
        1. compute the rule triggers;
        2. compute summary scores useful for logging;
        3. return a structured ethical assessment.
        """
        triggered_rules = get_triggered_rules(prediction, self.config)

        # If any rule is triggered, we consider the user vulnerable and in need of protection.
        is_vulnerable = len(triggered_rules) > 0

        # The final score combines the weighted risk estimate and the full
        # negative-emotion aggregate. This keeps the output informative even
        # when protection is not triggered.
        risk_score = max(
            weighted_risk_score(prediction, self.config),
            combined_negative_score(prediction, self.config),
        )

        rationale = build_rationale(
            prediction=prediction,
            config=self.config,
            triggered_rules=triggered_rules,
        )

        return EthicalAssessment(
            is_vulnerable=is_vulnerable,
            risk_score=risk_score,
            rationale=rationale,
            triggered_rules=triggered_rules,
        )
