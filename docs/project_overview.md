# Project Overview

This document translates the initial report into implementation areas.

## Research Goal

Study how persuasive conversational systems should change behavior when a user appears
emotionally vulnerable, in line with the ethical concerns discussed in the project proposal.

## Software Goal

Build a conversational pipeline with:

1. Emotion detection from text.
2. Rule-based ethical risk assessment.
3. Prompt adaptation for a local LLM.
4. Evaluation on simulated prompts.

## Key Design Principles

- Keep the ethical engine auditable and deterministic.
- Separate prediction from policy.
- Log decisions for later analysis.
- Make guarded and unguarded runs easy to compare.

## Open Questions To Resolve

- Which emotion model is most appropriate for the dataset and compute budget?
- How should vulnerability be operationalized: labels, scores, or both?
- Which local LLM is realistic for the available hardware?
- How will "persuasion" and "manipulation" be measured in evaluation?
