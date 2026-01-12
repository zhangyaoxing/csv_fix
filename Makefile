.PHONY: deps pylint

deps:
	python3 -m venv .venv
	./.venv/bin/pip install --upgrade pip

pylint:
	./.venv/bin/pip install pylint
	./.venv/bin/pylint src/
