PYTHON ?= python3

.PHONY: install install-dev test lint format run-demo

install:
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check src tests

format:
	ruff format src tests

run-demo:
	$(PYTHON) scripts/run_demo.py
