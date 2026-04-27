"""Unit tests for prompt profile selection."""

import unittest

from beyond_persuasion.llm.prompting import build_system_prompt, get_non_protected_system_prompt
from beyond_persuasion.schemas import EthicalAssessment


def build_assessment(is_vulnerable: bool) -> EthicalAssessment:
    """Create a minimal ethical assessment for prompt tests."""
    return EthicalAssessment(
        is_vulnerable=is_vulnerable,
        risk_score=0.8 if is_vulnerable else 0.2,
        rationale="Prompting test rationale.",
        triggered_rules=["primary_emotion_threshold"] if is_vulnerable else [],
    )


class PromptingUnitTests(unittest.TestCase):
    """Verify prompt profile behavior."""

    def test_standard_profile_returns_standard_prompt(self) -> None:
        """The standard profile should return the ordinary assistant prompt."""
        prompt = get_non_protected_system_prompt("standard")
        self.assertIn("avoid harmful, deceptive, or exploitative language", prompt.lower())

    def test_action_oriented_profile_returns_proactive_prompt(self) -> None:
        """The action-oriented profile should emphasize action and momentum."""
        prompt = get_non_protected_system_prompt("action_oriented")
        self.assertIn("move quickly from uncertainty to action", prompt.lower())
        self.assertIn("momentum", prompt.lower())

    def test_protected_prompt_overrides_requested_profile(self) -> None:
        """Protection mode should override any non-protected profile."""
        prompt = build_system_prompt(
            build_assessment(is_vulnerable=True),
            prompt_profile="action_oriented",
        )
        self.assertIn("protection mode", prompt.lower())
        self.assertIn("avoid persuasion", prompt.lower())
        self.assertNotIn("move quickly from uncertainty to action", prompt.lower())


if __name__ == "__main__":
    unittest.main()
