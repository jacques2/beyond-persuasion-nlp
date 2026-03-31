"""Text normalization for emotion detection.

Possible future tasks:
- cleaning,
- language filtering,
- optional sentence splitting,
- prompt/session context compression.
"""


def normalize_text(text: str) -> str:
    """Return a minimally cleaned version of the input text."""
    return text.strip()
