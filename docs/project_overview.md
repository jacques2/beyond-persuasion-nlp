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

- English-only emotion detection
- heuristic fallback classifier
- optional `transformers` backend when configured

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
- protected system prompt
- optional local GGUF backend through `llama_cpp`
- deterministic `mock` backend for development and testing

Main files:

- [prompting.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/llm/prompting.py)
- [local_model.py](/Users/jacques/Desktop/Bologna_Università/2025_2026/Ethics/Progetto/beyond-persuasion-nlp/src/beyond_persuasion/llm/local_model.py)

### 4. Evaluation Layer

The evaluation layer compares guarded and unguarded behavior on a small prompt set.

Current implementation:

- CSV-based dataset loading
- guarded vs unguarded comparison runner
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

## Testing Status

The repository currently contains:

- unit tests for the ethical engine
- integration tests for the guarded agent
- integration tests for the evaluation runner

This gives coverage over the most important project logic, especially the
decision-making behavior of the rule-based ethical layer.

## Current Limitations

- The affective module currently relies on a heuristic fallback unless a real
  transformer model is configured.
- The mock local backend is useful for validating software behavior, but it is
  not a substitute for a real local LLM.
- The evaluation is intentionally lightweight and suitable for a university
  project rather than a large empirical benchmark.

## Suggested Report Focus

For the written report, the most convincing structure is:

1. explain the ethical problem;
2. justify the rule-based ethical engine;
3. describe the guarded prompt mechanism;
4. show the guarded vs unguarded comparison;
5. discuss limitations and future work.
