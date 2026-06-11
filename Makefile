SRC=src
TESTS=tests

.PHONY=test lint type format clean
.SILENT=test lint type
IN_VENV=. .venv/bin/activate;

default: format lint type test

.venv/devdeps-up-to-date: .venv pyproject.toml
	$(IN_VENV)pip install poetry==2.4.1
	$(IN_VENV)poetry install --with test --with lint
	touch .venv/devdeps-up-to-date

.venv:
	python3 -m venv .venv

test: .venv/devdeps-up-to-date
	$(IN_VENV)python -m unittest $(TESTS) --failfast

lint: .venv/devdeps-up-to-date
	$(IN_VENV)python -m flake8 $(SRC)

type: .venv/devdeps-up-to-date
	$(IN_VENV)python -m mypy $(SRC)

format: .venv/devdeps-up-to-date
	$(IN_VENV)python -m black $(SRC)

clean:
	rm -r .venv
