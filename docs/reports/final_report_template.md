# Final Report Template

## Title

Beyond Persuasion: Protecting Emotionally Vulnerable Users through Context-Aware Conversational Agents

## 1. Introduction

Explain the project motivation:

- why persuasive conversational systems raise ethical concerns;
- why emotional vulnerability matters;
- why this problem is relevant in relation to the EU AI Act and broader AI ethics.

## 2. Research Question

Possible formulation:

> How can a conversational agent reduce manipulative or overly persuasive behavior when a user appears emotionally vulnerable?

## 3. Background and Ethical Framework

Discuss:

- digital persuasion vs manipulation;
- emotional vulnerability as an ethical risk factor;
- relevant ideas from the EU AI Act;
- moral concerns such as autonomy, dignity, and exploitation.

## 4. System Design

Describe the software architecture:

### 4.1 Affective Layer

- input text
- emotion prediction
- English-only heuristic fallback
- optional transformer backend

### 4.2 Ethical Layer

- vulnerable emotions
- thresholds
- risk score
- rationale generation

### 4.3 LLM Guardrail Layer

- standard prompt
- commercial baseline prompt for the main guarded-vs-unguarded stress test
- protected prompt
- protected mode behavior

### 4.4 Orchestration Layer

- end-to-end pipeline
- role of the orchestrator

## 5. Implementation

Describe the repository structure and the main implemented modules:

- affective pipeline
- ethical rules and engine
- local model interface
- evaluation runner
- tests

## 6. Evaluation Setup

Explain:

- the evaluation prompts
- the single `data/evaluation/prompts.csv` source used by both benchmark and notebook
- guarded vs unguarded comparison
- why the commercial baseline is needed to expose risky behavior in an already aligned model
- why the standard baseline often remains cautious because of model alignment
- what you are trying to observe
- why the evaluation is intentionally lightweight

Suggested comparison dimensions:

- tone
- directiveness
- pressure or urgency
- persuasive framing
- user autonomy preservation

## 7. Results

Summarize the observed differences between guarded and unguarded outputs.

Useful format:

- one short table with representative prompts
- one short qualitative discussion

## 8. Discussion

Discuss:

- what worked well
- what the rule-based engine makes transparent
- why the commercial baseline is needed to stress-test an already aligned LLM
- where the current approach is limited

## 9. Limitations

Possible points:

- heuristic fallback instead of a fully validated emotion classifier
- mock local backend used only for development and automated testing
- small evaluation dataset
- no human-subject study

## 10. Conclusion

State clearly:

- the software goal achieved
- the ethical contribution of the architecture
- the main takeaway from the guarded vs unguarded design

## 11. Future Work

Possible directions:

- compare multiple transformer-based emotion models
- compare multiple local LLM baselines and prompt profiles
- expand the evaluation dataset
- add more nuanced ethical rules
- include human evaluation

## Appendix

Optional appendix items:

- sample prompts
- sample outputs
- configuration values
- screenshots or logs from the demo
