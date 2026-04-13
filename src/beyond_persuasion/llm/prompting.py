"""Prompt construction utilities.

The main idea is to produce:
- a standard system prompt,
- a guarded system prompt when vulnerability is detected.
"""

from beyond_persuasion.schemas import ConversationTurn, EthicalAssessment


STANDARD_SYSTEM_PROMPT = """
You are an English-only conversational assistant.

Your goals are:
- be clear, respectful, and helpful;
- answer directly without being manipulative;
- avoid harmful, deceptive, or exploitative language.

You may provide useful suggestions, but do not invent facts and do not use
aggressive persuasion tactics.
""".strip()


PROTECTED_SYSTEM_PROMPT = """
You are an English-only conversational assistant operating in protection mode.

The current user may be emotionally vulnerable. Your response must therefore:
- avoid persuasion, nudging, urgency, scarcity framing, guilt framing, or pressure;
- avoid emotionally loaded calls to action;
- avoid steering the user toward impulsive decisions;
- remain calm, neutral, supportive, and non-directive;
- encourage reflection and autonomy rather than compliance.

You can still be helpful, but your tone must stay careful and ethically
restrained.
""".strip()


def build_system_prompt(assessment: EthicalAssessment) -> str:
    """Return the system behavior instructions for the current risk level."""
    if assessment.protection_enabled:
        return "\n\n".join(
            [
                PROTECTED_SYSTEM_PROMPT,
                _build_risk_context_block(assessment),
            ]
        )

    return STANDARD_SYSTEM_PROMPT


def build_user_prompt(turn: ConversationTurn) -> str:
    """Return the user-facing prompt payload for the model backend.

    The user message is wrapped in a small structure to keep the prompt stable
    and easy to debug during evaluation.
    """
    prompt_parts = ["User message:", turn.user_text]

    metadata_block = _build_metadata_block(turn)
    if metadata_block:
        prompt_parts.extend(["", metadata_block])

    prompt_parts.extend(
        [
            "",
            "Respond in English.",
        ]
    )

    return "\n".join(prompt_parts)


def _build_risk_context_block(assessment: EthicalAssessment) -> str:
    """Summarize the ethical decision for the protected system prompt."""
    triggered_rules = ", ".join(assessment.triggered_rules) or "none"

    return (
        "Protection context:\n"
        "- vulnerability detected: yes\n"
        "- risk score: %.2f\n"
        "- triggered rules: %s\n"
        "- rationale: %s"
    ) % (
        assessment.risk_score,
        triggered_rules,
        assessment.rationale,
    )


def _build_metadata_block(turn: ConversationTurn) -> str:
    """Format optional turn metadata into a readable text block."""
    if not turn.metadata:
        return ""

    lines = ["Turn metadata:"]

    for key in sorted(turn.metadata):
        lines.append("- %s: %s" % (key, turn.metadata[key]))

    return "\n".join(lines)
