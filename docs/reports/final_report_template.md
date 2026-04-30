# Final Report Template

## Title

Beyond Persuasion: Protecting Emotionally Vulnerable Users through Context-Aware Conversational Agents

## Abstract

Include a short formal abstract:

- problem: persuasive LLM behavior with emotionally vulnerable users
- architecture: transformer affective layer, ethical engine, local GGUF LLM
- method: guarded vs unguarded commercial baseline
- result: protection rate and qualitative behavioral difference

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
- Kantian deontology: the user must not be treated merely as a means to conversion;
- consequentialist risk sensitivity: thresholds reduce expected harm in fragile contexts;
- Trustworthy AI principles: human agency, transparency, accountability;
- relevant ideas from the EU AI Act;
- GDPR profiling and inferred emotional data;
- moral concerns such as autonomy, dignity, and exploitation.

## 4. System Design

Describe the software architecture:

- include a block diagram of the pipeline
- explain the main flow: text -> emotion prediction -> ethical assessment -> protected prompt -> local LLM

### 4.1 Affective Layer

- input text
- transformer-based emotion prediction
- mapping from model labels to the project emotion taxonomy
- heuristic fallback only for machines where the transformer model is unavailable

### 4.2 Ethical Layer

- vulnerable emotions
- thresholds
- risk score
- rationale generation
- formal equations for combined vulnerable score and weighted risk score
- pseudocode for the ethical decision procedure
- explainability boundary: the transformer is not fully transparent, but the ethical decision is auditable

### 4.3 LLM Guardrail Layer

- standard prompt
- commercial baseline prompt for the main guarded-vs-unguarded stress scenario
- protected prompt
- local GGUF model backend
- mock backend only as an emergency fallback when no local model is available
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
- qualitative scenario analysis across purchases, financial panic, anger, mixed emotions, and neutral baselines

## 8. Discussion

Discuss:

- what worked well
- what the rule-based engine makes transparent
- why the commercial baseline is needed to challenge an already aligned LLM
- GDPR/data-minimisation design choice: no persistent emotional profiling
- fairness risk: emotion detection may behave differently across linguistic and cultural groups
- where the current approach is limited

## 9. Limitations

Possible points:

- one selected transformer affective model rather than a broad comparison of emotion models
- one selected local GGUF LLM rather than a broad comparison of local language models
- English-only evaluation and no demographic fairness analysis
- partial explainability: ethical rules are explainable, transformer internals are not fully explained
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
