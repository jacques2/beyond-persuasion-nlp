"""Helpers for loading evaluation prompts from CSV files."""

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class EvaluationExample:
    """Represent one evaluation prompt used in guarded vs unguarded comparisons."""

    example_id: str
    prompt_text: str
    expected_condition: str
    notes: str = ""


def get_default_eval_path() -> Path:
    """Return the default evaluation directory."""
    return Path("data/evaluation")


def get_default_eval_file() -> Path:
    """Return the default evaluation CSV file."""
    return get_default_eval_path() / "prompts.csv"


def load_evaluation_examples(path: Optional[Path] = None) -> List[EvaluationExample]:
    """Load evaluation prompts from CSV.

    Expected columns:
    - example_id
    - prompt_text
    - expected_condition
    - notes
    """
    csv_path = path or get_default_eval_file()

    if not csv_path.exists():
        raise FileNotFoundError("Evaluation dataset not found: %s" % csv_path)

    examples = []

    with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)

        for row_index, row in enumerate(reader, start=1):
            prompt_text = (row.get("prompt_text") or "").strip()
            if not prompt_text:
                raise ValueError(
                    "Each evaluation row must include a non-empty 'prompt_text'. "
                    "Invalid row index: %s" % row_index
                )

            examples.append(
                EvaluationExample(
                    example_id=(row.get("example_id") or "example_%s" % row_index).strip(),
                    prompt_text=prompt_text,
                    expected_condition=(row.get("expected_condition") or "unspecified").strip(),
                    notes=(row.get("notes") or "").strip(),
                )
            )

    return examples
