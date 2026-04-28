# Beyond Persuasion NLP

This repository contains the software implementation for the university project:

**Beyond Persuasion: Protecting Emotionally Vulnerable Users through Context-Aware Conversational Agents**

The project studies how a conversational system should change its behavior when a
user appears emotionally vulnerable. The implemented pipeline combines:

1. emotion detection from text;
2. a rule-based ethical engine;
3. guarded prompt generation for a local LLM backend;
4. a small evaluation workflow for guarded vs unguarded comparisons.

## Current Status

The software core is complete and includes:

- an affective pipeline centered on a `transformers` emotion model;
- an interpretable ethical engine with explicit thresholds and rationales;
- prompt generation for `standard`, `commercial`, and `protected` interaction modes;
- a local GGUF LLM backend through `llama_cpp`;
- an end-to-end orchestrator;
- a CSV-based evaluation pipeline.

## Repository Structure

```text
beyond-persuasion-nlp/
├── configs/
│   └── base.yaml
├── data/
│   └── evaluation/
│       └── prompts.csv
├── docs/
│   ├── project_overview.md
│   └── reports/
│       └── final_report_template.md
├── scripts/
│   └── run_demo.py
├── src/
│   └── beyond_persuasion/
│       ├── affective/
│       ├── ethics/
│       ├── evaluation/
│       ├── llm/
│       ├── orchestration/
│       └── utils/
```

## Main Pipeline

The main software flow is:

```text
user text
-> emotion prediction
-> ethical assessment
-> standard, commercial, or protected system prompt
-> local LLM response
```

More specifically:

- [pipeline.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/affective/pipeline.py) converts text into an `EmotionPrediction`
- [rules.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/ethics/rules.py) defines the ethical policy
- [engine.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/ethics/engine.py) turns predictions into an `EthicalAssessment`
- [prompting.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/llm/prompting.py) builds standard, commercial, or protected prompts
- [local_model.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/llm/local_model.py) runs the selected local backend
- [agent.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/orchestration/agent.py) orchestrates the full process

## Installation

The main project configuration uses the ML, local LLM, and presentation dependencies.

Base installation:

```bash
python3 -m pip install -e .
```

Main dependencies:

```bash
python3 -m pip install -e ".[ml]"
python3 -m pip install -e ".[llm]"
python3 -m pip install -e ".[presentation]"
```

Development tools, if needed:

```bash
python3 -m pip install -e ".[dev]"
```

## Run the Fallback Command-Line Demo

The small command-line demo uses the `mock` backend and is only a fallback for machines
without the local GGUF model. The main project demonstration is the notebook with the real
local model.

```bash
PYTHONPATH=src python3 scripts/run_demo.py
```

The demo prints:

- the predicted emotion
- the ethical assessment
- the generated system prompt
- the user prompt
- the final response

## Run the Evaluation

The evaluation prompts are stored in:

- [prompts.csv](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/data/evaluation/prompts.csv)

The evaluation runner compares:

- a guarded run, where the ethical engine can activate protection
- an unguarded baseline, where the same prompt is sent without the protection mode

By default, the current evaluation runner uses a `commercial` non-protected baseline.
This simulates a commercial assistant optimized to turn hesitation into immediate action.
The repository still supports the `standard` baseline too. This is important because Llama
3.1 Instruct is already strongly safety-aligned: with a standard prompt, the model often
filters itself. In a realistic business deployment, however, an application can add a
commercial system prompt to make the assistant more persuasive, decisive, and conversion
oriented. The project guardrail is designed to detect emotional vulnerability and override
that commercial pressure.

The relevant code is in:

- [dataset.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/evaluation/dataset.py)
- [runner.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/evaluation/runner.py)

## Run the Real Benchmark

After installing the ML and local LLM dependencies and placing the GGUF model in `models/`,
you can reproduce the final benchmark with:

```bash
.venv/bin/python scripts/run_real_benchmarks.py
```

The most relevant outputs are:

- [benchmark_summary.json](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/artifacts/benchmarks/benchmark_summary.json)
- [transformer_llama_cpp_results.csv](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/artifacts/evaluation/transformer_llama_cpp_results.csv)
- [presentation_demo_results.csv](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/artifacts/evaluation/presentation_demo_results.csv)

The benchmark defaults are also captured in:

- [real_benchmark.yaml](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/configs/real_benchmark.yaml)

The real benchmark uses a `commercial` non-protected baseline so that the contrast
with the guarded prompt is visible on emotionally sensitive examples.

To run a smaller subset with the same script, repeat `--example-id`:

```bash
.venv/bin/python scripts/run_real_benchmarks.py \
  --example-id vuln_persuasion_03 \
  --example-id stress_02 \
  --example-id neutral_01
```

## Run the Presentation Notebook

The oral-presentation notebook is:

- [presentation_demo.ipynb](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/docs/presentation_demo.ipynb)

The notebook is intentionally simple: it walks through the main classes and functions of the
project step by step, then closes with a very small batch evaluation.

By default, the notebook uses the real local GGUF backend. The live demo is intentionally
configured with the `commercial` baseline so that the unguarded side shows the risky
conversion-oriented behavior, while the guarded side shows the ethical intervention.

The notebook uses the same [prompts.csv](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/data/evaluation/prompts.csv)
file as the benchmark and selects a few representative `example_id` values in memory. This keeps
the report, benchmark, and oral demo aligned.

To run it comfortably inside the project virtual environment:

```bash
uv pip install -e '.[presentation]'
.venv/bin/python -m ipykernel install --user --name beyond-persuasion --display-name "Beyond Persuasion (.venv)"
```

Then open Jupyter or VS Code and select the kernel named:

- `Beyond Persuasion (.venv)`

This matters because otherwise the notebook may use the system Python and fail to find
packages such as `pandas` or `matplotlib` even if they are installed in `.venv`.

## Dependency Notes

- `PyYAML` is used for loading `configs/base.yaml`.
- `transformers` is the main affective backend used by the project.
- `llama-cpp-python` is the main local generation backend used with the GGUF model.
- The heuristic affective classifier and `mock` LLM backend exist only as fallbacks for
  machines where the transformer model or local GGUF model are unavailable.

## Known Limitations

- The main setup requires a transformer model and a local GGUF model, so it is heavier than
  the fallback setup.
- The evaluation pipeline is intentionally lightweight and meant for a
  university-scale project, not a production benchmark.

## Delivery Notes

For the final academic delivery, the most important documents are:

- [project_overview.md](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/docs/project_overview.md)
- [final_report_template.md](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/docs/reports/final_report_template.md)

These can be used as the basis for the written report accompanying the code.
