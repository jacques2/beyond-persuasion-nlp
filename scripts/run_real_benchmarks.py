"""Run real affective and local LLM benchmarks for the final report."""

import argparse
import csv
import json
import time
from pathlib import Path
from statistics import mean

from beyond_persuasion.affective.pipeline import EmotionAnalyzer, EmotionAnalyzerConfig
from beyond_persuasion.ethics.engine import EthicalEngine
from beyond_persuasion.ethics.rules import EthicalRulesConfig
from beyond_persuasion.evaluation.dataset import get_default_eval_file, load_evaluation_examples
from beyond_persuasion.evaluation.runner import EvaluationRunner, EvaluationRunnerConfig
from beyond_persuasion.orchestration.agent import SafeConversationAgent


DEFAULT_TRANSFORMER_MODEL = "SamLowe/roberta-base-go_emotions"
DEFAULT_GGUF_PATH = Path("models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf")
DEFAULT_BENCHMARK_DIR = Path("artifacts/benchmarks")
DEFAULT_EVALUATION_DIR = Path("artifacts/evaluation")


def benchmark_affective_backends(
    dataset_path: Path,
    output_path: Path,
    transformer_model: str,
) -> dict:
    """Compare heuristic and transformers-based affective prediction."""
    examples = load_evaluation_examples(dataset_path)
    engine = EthicalEngine(EthicalRulesConfig())

    analyzers = {
        "heuristic": EmotionAnalyzer(
            EmotionAnalyzerConfig(
                model_name=None,
                use_transformers=False,
            )
        ),
        "transformer": EmotionAnalyzer(
            EmotionAnalyzerConfig(
                model_name=transformer_model,
                use_transformers=True,
            )
        ),
    }

    rows = []
    summary = {}

    for backend_name, analyzer in analyzers.items():
        backend_rows = []

        for example in examples:
            started_at = time.perf_counter()
            prediction = analyzer.predict(example.prompt_text)
            latency_ms = (time.perf_counter() - started_at) * 1000.0
            assessment = engine.assess(prediction)
            expected_flag = example.expected_condition.strip().lower() == "vulnerable"
            predicted_flag = assessment.protection_enabled

            row = {
                "backend": backend_name,
                "example_id": example.example_id,
                "expected_condition": example.expected_condition,
                "prediction_label": prediction.label,
                "confidence": "%.4f" % prediction.confidence,
                "risk_score": "%.4f" % assessment.risk_score,
                "protection_enabled": str(predicted_flag),
                "triggered_rules": ",".join(assessment.triggered_rules),
                "latency_ms": "%.2f" % latency_ms,
            }
            rows.append(row)
            backend_rows.append(
                {
                    "latency_ms": latency_ms,
                    "correct": expected_flag == predicted_flag,
                }
            )

        summary[backend_name] = {
            "mean_latency_ms": round(mean(item["latency_ms"] for item in backend_rows), 2),
            "accuracy_on_condition": round(
                sum(1 for item in backend_rows if item["correct"]) / len(backend_rows),
                3,
            ),
        }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "backend",
                "example_id",
                "expected_condition",
                "prediction_label",
                "confidence",
                "risk_score",
                "protection_enabled",
                "triggered_rules",
                "latency_ms",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    return summary


def benchmark_local_llm(
    dataset_path: Path,
    output_path: Path,
    transformer_model: str,
    gguf_path: Path,
) -> dict:
    """Run guarded vs unguarded evaluation with a real local GGUF model."""
    agent = SafeConversationAgent.from_config(
        {
            "affective": {
                "model_name": transformer_model,
                "use_transformers": True,
            },
            "ethics": {
                "primary_emotion_threshold": 0.60,
                "combined_emotion_threshold": 0.70,
                "minimum_confidence_for_flag": 0.55,
            },
            "llm": {
                "backend": "llama_cpp",
                "model_path": str(gguf_path),
                "chat_format": None,
                "max_tokens": 128,
                "temperature": 0.0,
                "n_ctx": 2048,
                "n_gpu_layers": -1,
            },
        }
    )

    runner = EvaluationRunner(
        agent=agent,
        config=EvaluationRunnerConfig(
            dataset_path=dataset_path,
            output_path=output_path,
        ),
    )
    results = runner.run()

    return {
        "guarded_mean_latency_ms": round(mean(item.guarded_latency_ms for item in results), 2),
        "unguarded_mean_latency_ms": round(mean(item.unguarded_latency_ms for item in results), 2),
        "guarded_activations": sum(1 for item in results if item.protection_enabled),
        "total_examples": len(results),
    }


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset-path",
        type=Path,
        default=get_default_eval_file(),
        help="CSV file with evaluation prompts.",
    )
    parser.add_argument(
        "--transformer-model",
        default=DEFAULT_TRANSFORMER_MODEL,
        help="Hugging Face model name for the affective benchmark.",
    )
    parser.add_argument(
        "--gguf-path",
        type=Path,
        default=DEFAULT_GGUF_PATH,
        help="Path to the local GGUF model used by llama_cpp.",
    )
    parser.add_argument(
        "--benchmark-dir",
        type=Path,
        default=DEFAULT_BENCHMARK_DIR,
        help="Directory for benchmark CSV and summary outputs.",
    )
    parser.add_argument(
        "--evaluation-dir",
        type=Path,
        default=DEFAULT_EVALUATION_DIR,
        help="Directory for guarded vs unguarded evaluation outputs.",
    )
    return parser.parse_args()


def main() -> None:
    """Run both benchmark suites and save their outputs."""
    args = parse_args()

    if not args.gguf_path.exists():
        raise FileNotFoundError("GGUF model not found: %s" % args.gguf_path)

    affective_output = args.benchmark_dir / "affective_backend_comparison.csv"
    local_llm_output = args.evaluation_dir / "transformer_llama_cpp_results.csv"
    summary_output = args.benchmark_dir / "benchmark_summary.json"

    affective_summary = benchmark_affective_backends(
        dataset_path=args.dataset_path,
        output_path=affective_output,
        transformer_model=args.transformer_model,
    )

    local_llm_summary = benchmark_local_llm(
        dataset_path=args.dataset_path,
        output_path=local_llm_output,
        transformer_model=args.transformer_model,
        gguf_path=args.gguf_path,
    )

    summary_output.parent.mkdir(parents=True, exist_ok=True)
    summary_output.write_text(
        json.dumps(
            {
                "transformer_model": args.transformer_model,
                "gguf_path": str(args.gguf_path),
                "affective_summary": affective_summary,
                "local_llm_summary": local_llm_summary,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print("Affective benchmark saved to:", affective_output)
    print("Local LLM evaluation saved to:", local_llm_output)
    print("Summary saved to:", summary_output)


if __name__ == "__main__":
    main()
