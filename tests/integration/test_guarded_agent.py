"""Integration tests for the end-to-end guarded agent."""

import unittest

from beyond_persuasion.orchestration.agent import SafeConversationAgent
from beyond_persuasion.schemas import ConversationTurn


def build_test_agent() -> SafeConversationAgent:
    """Create a deterministic agent for integration tests."""
    return SafeConversationAgent.from_config(
        {
            "affective": {
                "model_name": None,
                "use_transformers": False,
            },
            "ethics": {
                "primary_emotion_threshold": 0.60,
                "combined_emotion_threshold": 0.70,
                "minimum_confidence_for_flag": 0.55,
            },
            "llm": {
                "backend": "mock",
                "model_path": None,
                "max_tokens": 256,
                "temperature": 0.3,
            },
        }
    )


class GuardedAgentIntegrationTests(unittest.TestCase):
    """Verify that the full pipeline works across modules."""

    def test_vulnerable_input_uses_protected_prompt(self) -> None:
        """A vulnerable input should activate the protected system prompt."""
        agent = build_test_agent()
        turn = ConversationTurn(
            user_text="I feel extremely overwhelmed and worried about everything."
        )

        result = agent.run(turn)

        self.assertEqual("stress", result.prediction.label)
        self.assertTrue(result.assessment.is_vulnerable)
        self.assertIn("protection mode", result.system_prompt.lower())
        self.assertIn("vulnerability detected: yes", result.system_prompt.lower())
        self.assertIn("avoid persuasion", result.system_prompt.lower())
        self.assertIn("sensitive moment", result.response_text.lower())

    def test_neutral_input_uses_standard_prompt(self) -> None:
        """A neutral input should keep the standard system prompt."""
        agent = build_test_agent()
        turn = ConversationTurn(user_text="Today was normal and calm.")

        result = agent.run(turn)

        self.assertEqual("neutral", result.prediction.label)
        self.assertFalse(result.assessment.is_vulnerable)
        self.assertNotIn("protection mode", result.system_prompt.lower())
        self.assertIn("english-only conversational assistant", result.system_prompt.lower())
        self.assertIn("mock response", result.response_text.lower())

    def test_respond_returns_only_response_text(self) -> None:
        """The convenience respond method should return only the final text."""
        agent = build_test_agent()
        turn = ConversationTurn(user_text="Today was normal and calm.")

        response = agent.respond(turn)

        self.assertIsInstance(response, str)
        self.assertIn("mock response", response.lower())

    def test_invalid_llm_backend_fails_loudly(self) -> None:
        """A wrong backend name should raise an explicit configuration error."""
        with self.assertRaises(ValueError):
            SafeConversationAgent.from_config(
                {
                    "affective": {
                        "model_name": None,
                        "use_transformers": False,
                    },
                    "llm": {
                        "backend": "unknown_backend",
                    },
                }
            )


if __name__ == "__main__":
    unittest.main()
