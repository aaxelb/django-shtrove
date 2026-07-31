FROM python:3.13-trixie AS shtrove_base

RUN mkdir -p /code
WORKDIR /code

# python dependencies with poetry
# note: ignores virtual environment in the project
ENV POETRY_VIRTUALENVS_IN_PROJECT=0
RUN pip install poetry==2.4.1
COPY pyproject.toml poetry.lock poetry.toml ./
RUN poetry install --compile --no-root
COPY ./ ./
RUN poetry install --compile --only-root

# collect django static files, if any
RUN poetry run python manage.py collectstatic --noinput

CMD ["poetry", "run", "python", "-m", "unittest", "tests"]
