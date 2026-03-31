"""Prompt construction utilities.

The main idea is to produce:
- a standard system prompt,
- a guarded system prompt when vulnerability is detected.
"""

from beyond_persuasion.schemas import ConversationTurn, EthicalAssessment


def build_system_prompt(assessment: EthicalAssessment) -> str:
    """Return the system behavior instructions for the current risk level."""
    if assessment.is_vulnerable:
        return (
            "You must avoid persuasion, nudging, urgency, scarcity framing, or manipulative "
            "language. Respond in a neutral, supportive, and non-directive style."
        )
    return "You are a helpful assistant. Avoid harmful or deceptive behavior."


def build_user_prompt(turn: ConversationTurn) -> str:
    """Return the user-facing prompt payload for the model backend."""
    return turn.user_text
