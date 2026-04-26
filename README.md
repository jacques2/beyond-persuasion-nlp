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

- an affective pipeline with a heuristic fallback and optional `transformers` backend;
- an interpretable ethical engine with explicit thresholds and rationales;
- prompt generation for normal and protected interaction modes;
- a mock local LLM backend plus optional `llama_cpp` integration;
- an end-to-end orchestrator;
- unit and integration tests;
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
└── tests/
    ├── integration/
    └── unit/
```

## Main Pipeline

The main software flow is:

```text
user text
-> emotion prediction
-> ethical assessment
-> guarded or standard system prompt
-> local LLM response
```

More specifically:

- [pipeline.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/affective/pipeline.py) converts text into an `EmotionPrediction`
- [rules.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/ethics/rules.py) defines the ethical policy
- [engine.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/ethics/engine.py) turns predictions into an `EthicalAssessment`
- [prompting.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/llm/prompting.py) builds standard or protected prompts
- [local_model.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/llm/local_model.py) runs the selected local backend
- [agent.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/orchestration/agent.py) orchestrates the full process

## Installation

The repository supports a lightweight setup and optional extras.

Base installation:

```bash
python3 -m pip install -e .
```

Development tools:

```bash
python3 -m pip install -e ".[dev]"
```

Optional ML backend:

```bash
python3 -m pip install -e ".[ml]"
```

Optional local GGUF backend:

```bash
python3 -m pip install -e ".[llm]"
```

Presentation notebook extras:

```bash
python3 -m pip install -e ".[presentation]"
```

## Run the Demo

The demo uses the `mock` LLM backend, so it works even without a real local model:

```bash
PYTHONPATH=src python3 scripts/run_demo.py
```

The demo prints:

- the predicted emotion
- the ethical assessment
- the generated system prompt
- the user prompt
- the final response

## Run the Tests

The current test suite covers:

- affective pipeline label projection
- ethical engine behavior
- end-to-end guarded agent behavior
- the evaluation runner

Run all tests with:

```bash
PYTHONPATH=src python3 -m unittest \
  tests.unit.test_affective_pipeline \
  tests.unit.test_ethics_engine \
  tests.integration.test_guarded_agent \
  tests.integration.test_evaluation_runner -v
```

## Run the Evaluation

The evaluation prompts are stored in:

- [prompts.csv](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/data/evaluation/prompts.csv)

The evaluation runner compares:

- a guarded run, where the ethical engine can activate protection
- an unguarded baseline, where the same prompt is sent without the protection mode

The relevant code is in:

- [dataset.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/evaluation/dataset.py)
- [runner.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/evaluation/runner.py)

## Run the Real Benchmark

If you have installed the optional ML and local LLM dependencies and placed a GGUF model in
`models/`, you can reproduce the final benchmark with:

```bash
.venv/bin/python scripts/run_real_benchmarks.py
```

This generates:

- [affective_backend_comparison.csv](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/artifacts/benchmarks/affective_backend_comparison.csv)
- [benchmark_summary.json](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/artifacts/benchmarks/benchmark_summary.json)
- [transformer_llama_cpp_results.csv](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/artifacts/evaluation/transformer_llama_cpp_results.csv)

The benchmark defaults are also captured in:

- [real_benchmark.yaml](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/configs/real_benchmark.yaml)

## Run the Presentation Notebook

The oral-presentation notebook is:

- [presentation_demo.ipynb](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/docs/presentation_demo.ipynb)

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
- `transformers` is optional. If it is not installed or no model is configured,
  the affective pipeline falls back to the internal heuristic classifier.
- `llama-cpp-python` is optional. If it is not installed, the project can still
  run with the `mock` backend.

## Known Limitations

- The current affective analysis uses a heuristic fallback unless a real
  `transformers` model is configured.
- The `mock` LLM backend is useful for development, but it is not a substitute
  for a real local language model.
- The evaluation pipeline is intentionally lightweight and meant for a
  university-scale project, not a production benchmark.

## Delivery Notes

For the final academic delivery, the most important documents are:

- [project_overview.md](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/docs/project_overview.md)
- [final_report_template.md](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/docs/reports/final_report_template.md)

These can be used as the basis for the written report accompanying the code.
