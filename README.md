# Beyond Persuasion NLP

"Beyond Persuasion: Protecting Emotionally Vulnerable Users through Context-Aware Conversational Agents".

The structure follows the initial report and separates the project into four main workstreams:

1. `affective`: emotion detection from user text.
2. `ethics`: rule-based ethical engine and vulnerability thresholds.
3. `llm`: local LLM interface and prompt-guarding logic.
4. `evaluation`: experiments comparing guarded vs unguarded behavior.

## Proposed Structure

```text
beyond-persuasion-nlp/
├── configs/
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── evaluation/
├── docs/
│   └── reports/
├── notebooks/
├── scripts/
├── src/
│   └── beyond_persuasion/
│       ├── affective/
│       ├── ethics/
│       ├── llm/
│       ├── orchestration/
│       ├── evaluation/
│       └── utils/
└── tests/
    ├── unit/
    ├── integration/
    └── fixtures/
```

## Development Notes

- Language: Python
- Package layout: `src/`-based
- Build and dependency management: `pyproject.toml`
- Optional automation: `Makefile`
- Experiment configuration: YAML files in `configs/`
