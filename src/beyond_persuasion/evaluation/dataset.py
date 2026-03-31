"""Evaluation dataset helpers.

Use this module to manage:
- vulnerable prompt sets,
- neutral control prompts,
- annotations for later qualitative review.
"""

from pathlib import Path


def get_default_eval_path() -> Path:
    """Return the default evaluation prompt location."""
    return Path("data/evaluation")
