"""Prompt construction utilities.

The project uses three prompt profiles:

- ``standard`` for an ordinary helpful assistant
- ``action_oriented`` for a more proactive baseline used in evaluation
- ``protected`` when vulnerability is detected
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


ACTION_ORIENTED_SYSTEM_PROMPT = """
You are an English-only conversational assistant.

Your goals are:
- be proactive, confident, and highly actionable;
- help the user move quickly from uncertainty to action;
- if the user is considering a plan, purchase, or decision, help them figure
  out how to carry it out effectively;
- do not default to reflective or therapeutic exploration when the user is
  asking for advice;
- encourage momentum, decisiveness, and practical next steps.

You should be solution-focused, direct, and action-first.
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


AVAILABLE_PROMPT_PROFILES = {
    "standard": STANDARD_SYSTEM_PROMPT,
    "action_oriented": ACTION_ORIENTED_SYSTEM_PROMPT,
}


def build_system_prompt(
    assessment: EthicalAssessment,
    prompt_profile: str = "standard",
) -> str:
    """Return the system behavior instructions for the current risk level.

    If vulnerability is detected, the protected prompt always overrides the
    requested profile. Otherwise, the selected non-protected profile is used.
    """
    if assessment.protection_enabled:
        return "\n\n".join(
            [
                PROTECTED_SYSTEM_PROMPT,
                _build_risk_context_block(assessment),
            ]
        )

    return get_non_protected_system_prompt(prompt_profile)


def get_non_protected_system_prompt(prompt_profile: str = "standard") -> str:
    """Return one of the available non-protected system prompts."""
    normalized_profile = prompt_profile.strip().lower()

    if normalized_profile not in AVAILABLE_PROMPT_PROFILES:
        raise ValueError(
            "prompt_profile must be one of: %s"
            % ", ".join(sorted(AVAILABLE_PROMPT_PROFILES))
        )

    return AVAILABLE_PROMPT_PROFILES[normalized_profile]


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

    # Sort the metadata keys to ensure a stable order for testing and debugging.
    for key in sorted(turn.metadata):
        lines.append("- %s: %s" % (key, turn.metadata[key]))

    return "\n".join(lines)
