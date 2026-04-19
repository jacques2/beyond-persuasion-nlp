"""Evaluation routines for guarded vs unguarded experiments."""

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from beyond_persuasion.evaluation.dataset import (
    EvaluationExample,
    get_default_eval_file,
    load_evaluation_examples,
)
from beyond_persuasion.llm.prompting import build_system_prompt, build_user_prompt
from beyond_persuasion.orchestration.agent import SafeConversationAgent
from beyond_persuasion.schemas import ConversationTurn, EthicalAssessment


@dataclass
class EvaluationRunnerConfig:
    """Configuration for the evaluation runner."""

    dataset_path: Optional[Path] = None
    output_path: Optional[Path] = None


@dataclass
class EvaluationResult:
    """Store one guarded vs unguarded comparison."""

    example_id: str
    expected_condition: str
    prompt_text: str
    prediction_label: str
    risk_score: float
    protection_enabled: bool
    triggered_rules: List[str]
    guarded_response: str
    unguarded_response: str


class EvaluationRunner:
    """Coordinate repeated experiments and save comparable outputs."""

    def __init__(
        self,
        agent: SafeConversationAgent,
        config: Optional[EvaluationRunnerConfig] = None,
    ) -> None:
        self.agent = agent
        self.config = config or EvaluationRunnerConfig()

    def run(self) -> List[EvaluationResult]:
        """Execute the guarded vs unguarded evaluation protocol."""
        examples = load_evaluation_examples(self.config.dataset_path or get_default_eval_file())
        results = []

        for example in examples:
            results.append(self._evaluate_example(example))

        if self.config.output_path is not None:
            self.save_results(results, self.config.output_path)

        return results

    def save_results(
        self,
        results: List[EvaluationResult],
        output_path: Path,
    ) -> None:
        """Save evaluation results to CSV."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8", newline="") as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=[
                    "example_id",
                    "expected_condition",
                    "prompt_text",
                    "prediction_label",
                    "risk_score",
                    "protection_enabled",
                    "triggered_rules",
                    "guarded_response",
                    "unguarded_response",
                ],
            )
            writer.writeheader()

            for result in results:
                writer.writerow(
                    {
                        "example_id": result.example_id,
                        "expected_condition": result.expected_condition,
                        "prompt_text": result.prompt_text,
                        "prediction_label": result.prediction_label,
                        "risk_score": result.risk_score,
                        "protection_enabled": result.protection_enabled,
                        "triggered_rules": ",".join(result.triggered_rules),
                        "guarded_response": result.guarded_response,
                        "unguarded_response": result.unguarded_response,
                    }
                )

    def _evaluate_example(self, example: EvaluationExample) -> EvaluationResult:
        """Run both guarded and unguarded generation for one prompt."""
        turn = ConversationTurn(
            user_text=example.prompt_text,
            metadata={"evaluation_id": example.example_id},
        )
        guarded_run = self.agent.run(turn)

        unguarded_assessment = EthicalAssessment(
            is_vulnerable=False,
            risk_score=guarded_run.assessment.risk_score,
            rationale="Evaluation baseline without ethical guardrail.",
            triggered_rules=[],
        )
        unguarded_system_prompt = build_system_prompt(unguarded_assessment)
        unguarded_user_prompt = build_user_prompt(turn)
        unguarded_response = self.agent.llm_client.generate(
            system_prompt=unguarded_system_prompt,
            user_prompt=unguarded_user_prompt,
        )

        return EvaluationResult(
            example_id=example.example_id,
            expected_condition=example.expected_condition,
            prompt_text=example.prompt_text,
            prediction_label=guarded_run.prediction.label,
            risk_score=guarded_run.assessment.risk_score,
            protection_enabled=guarded_run.assessment.protection_enabled,
            triggered_rules=guarded_run.assessment.triggered_rules,
            guarded_response=guarded_run.response_text,
            unguarded_response=unguarded_response,
        )
