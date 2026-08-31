SRC=src

.PHONY=check test shtrove_test django_shtrove_test format lint clean
.SILENT=lint
IN_VENV=. .venv/bin/activate;

default: format lint test

check: lint test

test: shtrove_test django_shtrove_test

shtrove_test: .venv/devdeps-up-to-date
	$(IN_VENV)python -m unittest discover -s shtrove --failfast

django_shtrove_test: .venv/devdeps-up-to-date
	$(IN_VENV)python src/django_shtrove/manage.py test --failfast

format: .venv/devdeps-up-to-date
	$(IN_VENV)python -m black $(SRC)

lint: .venv/devdeps-up-to-date
	$(IN_VENV)python -m black --check --quiet $(SRC)
	$(IN_VENV)python -m flake8 $(SRC)
	$(IN_VENV)python -m mypy $(SRC)

clean:
	rm -r .venv

.venv/devdeps-up-to-date: .venv pyproject.toml
	$(IN_VENV)pip install poetry==2.4.1
	$(IN_VENV)poetry install --with test --with lint
	touch .venv/devdeps-up-to-date

.venv:
	python3 -m venv .venv
