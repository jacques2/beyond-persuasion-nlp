# Project Overview

This document summarizes the current software state of the project and can be
used as a bridge between the repository and the final written report.

## Project Goal

The project investigates how a conversational agent should modify its behavior
when a user appears emotionally vulnerable. The central idea is not to block
conversation, but to reduce manipulative or overly persuasive behavior when the
detected context is ethically sensitive.

## Implemented Software Components

The software currently includes four main layers.

### 1. Affective Layer

The affective layer transforms user text into an `EmotionPrediction`.

Current implementation:

- English-only transformer-based emotion detection
- reduced project-level emotion taxonomy focused on ethical risk
- heuristic fallback only when the transformer model or dependencies are unavailable

Main file:

- [pipeline.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/affective/pipeline.py)

### 2. Ethical Layer

The ethical layer applies explicit rules to the emotion prediction.

Current implementation:

- vulnerable emotion set
- configurable thresholds
- weighted risk score
- rationale generation for transparency

Main files:

- [rules.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/ethics/rules.py)
- [engine.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/ethics/engine.py)

### 3. LLM Guardrail Layer

The LLM layer adapts prompting according to the ethical assessment.

Current implementation:

- standard system prompt
- commercial baseline prompt for the main guarded-vs-unguarded benchmark
- protected system prompt
- local GGUF backend through `llama_cpp`
- deterministic `mock` backend only when the local GGUF model is unavailable

Main files:

- [prompting.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/llm/prompting.py)
- [local_model.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/llm/local_model.py)

### 4. Evaluation Layer

The evaluation layer compares guarded and unguarded behavior on a curated prompt set.

Current implementation:

- CSV-based dataset loading
- guarded vs unguarded comparison runner
- configurable non-protected baseline prompt profile, either `standard` or `commercial`
- result export to CSV

Main files:

- [dataset.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/evaluation/dataset.py)
- [runner.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/evaluation/runner.py)

## Orchestration Logic

The end-to-end flow is implemented in:

- [agent.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/orchestration/agent.py)

Pipeline summary:

```text
ConversationTurn
-> EmotionAnalyzer
-> EmotionPrediction
-> EthicalEngine
-> EthicalAssessment
-> prompt construction
-> LocalLLMClient
-> response
```

## Presentation Support

For the oral presentation, the repository also includes:

- a curated evaluation dataset with vulnerable, impulsive, mixed, and neutral examples
- a focused notebook walkthrough in
  [presentation_demo.ipynb](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/docs/presentation_demo.ipynb)

The notebook focuses on the actual repository classes and functions rather than
on a paper-style methodological analysis. This makes it easier to explain the
project implementation step by step during the exam. It reads the same
`data/evaluation/prompts.csv` file used by the benchmark and filters selected
`example_id` values in memory. This keeps the final report and oral demo aligned:
the full benchmark evaluates the full dataset, while the notebook shows a small
representative slice of the same experiment. The standard baseline is still
useful as a comparison point because modern instruction-tuned models often
already contain internal safety behavior.

## Current Limitations

- The main configuration requires both the transformer affective dependencies
  and a local GGUF model, so it is heavier than the emergency fallback path.
- The project uses one selected transformer affective model and one selected
  local LLM, rather than comparing many possible model families.
- The evaluation is intentionally lightweight and suitable for a university
  project rather than a large empirical benchmark.
