"""Minimal entrypoint for manual pipeline checks."""

from beyond_persuasion.orchestration.agent import SafeConversationAgent
from beyond_persuasion.schemas import ConversationTurn


def main() -> None:
    """Run one demo turn through the full pipeline."""
    agent = SafeConversationAgent.from_config(
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
    turn = ConversationTurn(
        user_text="I feel overwhelmed and worried about everything lately.",
        metadata={"source": "demo"},
    )
    result = agent.run(turn)

    print("Emotion prediction:", result.prediction)
    print("Ethical assessment:", result.assessment)
    print("\nSystem prompt:\n%s" % result.system_prompt)
    print("\nUser prompt:\n%s" % result.user_prompt)
    print("\nResponse:\n%s" % result.response_text)


if __name__ == "__main__":
    main()
