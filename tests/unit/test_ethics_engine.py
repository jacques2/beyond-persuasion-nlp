"""Unit tests for the rule-based ethical engine.

These tests focus on the core policy decisions:
- clear vulnerable signals should trigger protection;
- neutral signals should not trigger protection;
- aggregated negative emotions can trigger protection even without a strong
  single dominant emotion.
"""

import unittest

from beyond_persuasion.ethics.engine import EthicalEngine
from beyond_persuasion.schemas import EmotionPrediction


class EthicalEngineTests(unittest.TestCase):
    """Verify the main decisions produced by the ethical engine."""

    def setUp(self) -> None:
        self.engine = EthicalEngine()

    def test_primary_vulnerable_emotion_triggers_protection(self) -> None:
        """A strong vulnerable dominant emotion should activate protection."""
        prediction = EmotionPrediction(
            label="sadness",
            confidence=0.82,
            scores={
                "sadness": 0.82,
                "anger": 0.03,
                "fear": 0.02,
                "stress": 0.03,
                "neutral": 0.10,
            },
        )

        assessment = self.engine.assess(prediction)

        self.assertTrue(assessment.is_vulnerable)
        self.assertIn("primary_emotion_threshold", assessment.triggered_rules)
        self.assertIn("combined_negative_emotions", assessment.triggered_rules)
        self.assertIn("dominant emotion 'sadness'", assessment.rationale)
        self.assertGreaterEqual(assessment.risk_score, 0.82)

    def test_neutral_prediction_does_not_trigger_protection(self) -> None:
        """A neutral prediction should keep protection disabled."""
        prediction = EmotionPrediction(
            label="neutral",
            confidence=0.88,
            scores={
                "sadness": 0.03,
                "anger": 0.02,
                "fear": 0.02,
                "stress": 0.05,
                "neutral": 0.88,
            },
        )

        assessment = self.engine.assess(prediction)

        self.assertFalse(assessment.is_vulnerable)
        self.assertEqual([], assessment.triggered_rules)
        self.assertIn("No protection rule was triggered", assessment.rationale)
        self.assertLess(assessment.risk_score, 0.20)

    def test_low_confidence_single_emotion_does_not_trigger_by_itself(self) -> None:
        """A weak vulnerable signal should not trigger protection alone."""
        prediction = EmotionPrediction(
            label="sadness",
            confidence=0.40,
            scores={
                "sadness": 0.40,
                "anger": 0.05,
                "fear": 0.05,
                "stress": 0.05,
                "neutral": 0.45,
            },
        )

        assessment = self.engine.assess(prediction)

        self.assertFalse(assessment.is_vulnerable)
        self.assertEqual([], assessment.triggered_rules)

    def test_combined_negative_emotions_can_trigger_protection(self) -> None:
        """Several medium negative emotions can trigger protection together."""
        prediction = EmotionPrediction(
            label="sadness",
            confidence=0.35,
            scores={
                "sadness": 0.35,
                "anger": 0.00,
                "fear": 0.36,
                "stress": 0.00,
                "neutral": 0.29,
            },
        )

        assessment = self.engine.assess(prediction)

        self.assertTrue(assessment.is_vulnerable)
        self.assertEqual(["combined_negative_emotions"], assessment.triggered_rules)
        self.assertIn("aggregate threshold", assessment.rationale)
        self.assertAlmostEqual(0.71, assessment.risk_score, places=6)


if __name__ == "__main__":
    unittest.main()
