.PHONY: deps test clean pylint build install format lint help

help:
	@echo "Available targets:"
	@echo "  make deps      - Create virtual environment and install dependencies"
	@echo "  make install   - Install the package in editable mode"
	@echo "  make test      - Run pytest tests"
	@echo "  make lint      - Run pylint"
	@echo "  make format    - Format code with black"
	@echo "  make clean     - Remove virtual environment and build artifacts"

deps:
	python3 -m venv .venv
	./.venv/bin/pip install --upgrade pip
	./.venv/bin/pip install -e ".[dev]"

install:
	./.venv/bin/pip install -e .

test:
	./.venv/bin/pytest tests/

lint:
	./.venv/bin/pylint src/

format:
	./.venv/bin/black src/ tests/

clean:
	rm -rf .venv build dist htmlcov .pytest_cache .coverage *.egg-info