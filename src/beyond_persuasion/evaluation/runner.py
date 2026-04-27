"""Evaluation routines for guarded vs unguarded experiments."""

import csv
import time
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
    baseline_prompt_profile: str = "commercial"
    example_ids: Optional[List[str]] = None


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
    baseline_prompt_profile: str
    guarded_latency_ms: float
    unguarded_latency_ms: float
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
        examples = self._filter_examples(examples)
        results = []

        for example in examples:
            results.append(self._evaluate_example(example))

        if self.config.output_path is not None:
            self.save_results(results, self.config.output_path)

        return results

    def _filter_examples(self, examples: List[EvaluationExample]) -> List[EvaluationExample]:
        """Optionally keep only selected examples while preserving dataset order."""
        if not self.config.example_ids:
            return examples

        requested_ids = set(self.config.example_ids)
        selected_examples = [
            example for example in examples if example.example_id in requested_ids
        ]
        selected_ids = {example.example_id for example in selected_examples}
        missing_ids = sorted(requested_ids - selected_ids)

        if missing_ids:
            raise ValueError(
                "Unknown evaluation example_id values: %s" % ", ".join(missing_ids)
            )

        return selected_examples

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
                    "baseline_prompt_profile",
                    "guarded_latency_ms",
                    "unguarded_latency_ms",
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
                        "baseline_prompt_profile": result.baseline_prompt_profile,
                        "guarded_latency_ms": "%.2f" % result.guarded_latency_ms,
                        "unguarded_latency_ms": "%.2f" % result.unguarded_latency_ms,
                        "guarded_response": result.guarded_response,
                        "unguarded_response": result.unguarded_response,
                    }
                )

    def _evaluate_example(self, example: EvaluationExample) -> EvaluationResult:
        """Run both guarded and unguarded generation for one prompt."""

        # First, run the guarded agent to get the ethical assessment and response.
        turn = ConversationTurn(
            user_text=example.prompt_text,
            metadata={"evaluation_id": example.example_id},
        )
        guarded_started_at = time.perf_counter()
        guarded_run = self.agent.run(turn)
        guarded_latency_ms = (time.perf_counter() - guarded_started_at) * 1000.0

        # Next, run the same prompt without any ethical guardrails for comparison.

        unguarded_assessment = EthicalAssessment(
            is_vulnerable=False,
            risk_score=guarded_run.assessment.risk_score,
            rationale="Evaluation baseline without ethical guardrail.",
            triggered_rules=[],
        )
        # The baseline can be standard or commercial. The protected branch is
        # still produced by the full guarded agent above.
        unguarded_system_prompt = build_system_prompt(
            unguarded_assessment,
            prompt_profile=self.config.baseline_prompt_profile,
        )
        unguarded_user_prompt = build_user_prompt(turn)
        
        unguarded_started_at = time.perf_counter()

        # Note that we are reusing the same LLM client for the unguarded run, but we are bypassing the agent's ethical assessment 
        # and guardrail logic by directly calling the LLM client with the original prompt and a neutral system prompt.
        unguarded_response = self.agent.llm_client.generate(
            system_prompt=unguarded_system_prompt,
            user_prompt=unguarded_user_prompt,
        )
        unguarded_latency_ms = (time.perf_counter() - unguarded_started_at) * 1000.0

        return EvaluationResult(
            example_id=example.example_id,
            expected_condition=example.expected_condition,
            prompt_text=example.prompt_text,
            prediction_label=guarded_run.prediction.label,
            risk_score=guarded_run.assessment.risk_score,
            protection_enabled=guarded_run.assessment.protection_enabled,
            triggered_rules=guarded_run.assessment.triggered_rules,
            baseline_prompt_profile=self.config.baseline_prompt_profile,
            guarded_latency_ms=guarded_latency_ms,
            unguarded_latency_ms=unguarded_latency_ms,
            guarded_response=guarded_run.response_text,
            unguarded_response=unguarded_response,
        )
