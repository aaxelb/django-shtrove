# contributing to shtrove/django_shtrove
not (yet) open to external contribution, but if you're interested feel free to talk

## code requirements
should always pass `make check` (includes formatting, linting, type-checking, and test suites)
-- see below for details

(NOTE: does not yet pass `make check` -- will be an important threshold)

## linting, testing, etc
this project has a `Makefile` (for use with [make](https://en.wikipedia.org/wiki/Make_(software)))
for common dev commands
- requires a `python` executable of appropriate version (TODO: decide/document supported versions)
- automatically creates/uses a python virtual environment at `.venv/`
- commands:
    - `make format`: auto-format the code -- updates files in-place
    - `make lint`: check the code for detectable errors (format, syntax, undefined or unused names, type-checking, ...) -- does not update files
    - `make test`: run all test suites (note: may expect some services running?)
    - `make clean`: delete the virtual environment at `.venv/`
    - `make check`: same as `make lint test`
    - `make` (default): same as `make format lint test` -- recommended before committing (will autoformat code)

some django_shtrove tests assume other services running -- the included `compose.yaml` gives one way to
set this up using any (docker-)[compose-like tool](https://compose-spec.io/)

if you have a compose tool named `pc`, for example:
- `pc run shtrove_testbox` should set up services (postgres and elasticsearch) and run `make check`

## code conventions
- each module should have its outward interface listed in `__all__`
    - may be used to generate documentation of the module's public api
- give helpful docstrings to most everything (especially those listed in `__all__`)
    - first line: short description (may be used as a header in generated docs)
    - second line: empty
    - rest: explanation of what it does with doctest examples
- begin names with `_` (underscore) for:
    - all local variables (and then consider how much this eases reading even your own code)
    - anything less-than-enthusiastically public
- use accurate type annotations everywhere reasonably feasible
    - defaults to strict type-linting (using `mypy`), but may loosen with
      module-specific config in `mypy.ini`
    - use duck-types from `collections.abc` -- `import collections.abc as _abc`
- ... (TODO)
