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
    - `make format`: auto-format the code -- modifies files in-place
    - `make lint`: check the code for detectable errors (format, syntax, undefined or unused names, type-checking, ...) -- does not modify files
    - `make test`: run all test suites (note: may expect some services running?)
    - `make clean`: delete the virtual environment at `.venv/`
    - `make check`: same as `make lint test`
    - `make` (default): same as `make format lint test` -- recommended before committing (will autoformat code)

some django_shtrove tests assume other services running -- the included `compose.yaml` gives one way to
set this up using any (docker-)[compose-like tool](https://compose-spec.io/)

if you have a compose tool named `pc`, for example:
- `pc run shtrove_testbox` should set up services (postgres and elasticsearch) and run `make check`

## code conventions
- choose names thoughtfully
    - try to consider what a name might convey in various contexts -- avoid unhelpful collisions
    - whenever a name is not meant for use outside its file, prefix with `_` (underscore)
      -- this includes all local variables (try it and see how much easier to understand)
    - a name prefixed `each_` indicates something meant to be iterated on only once,
      like an iterator or a generator function
      ```
      def each_thing() -> _abc.Iterator[Thing]:
          yield Thing(1)
          yield Thing(2)
      ```
- use accurate type annotations everywhere reasonably feasible
    - especially for public interface (and then try to avoid breaking type changes)
    - `make lint` defaults to strict type-linting (using `mypy`), but you may loosen constraints
      with module-specific config in `mypy.ini` -- avoid getting too stuck when type annotations
      are less-reasonably feasible
    - use duck-types from `collections.abc` -- `import collections.abc as _abc`
      - prefer more permissive types (like `_abc.Iterable[T]`) when multiple implementations
- each module should have its outward interface listed in `__all__`
    - may be used to generate documentation of the module's public interface
- give helpful docstrings to most everything (especially public interfaces)
    - often helpful to follow [python docstring conventions](https://peps.python.org/pep-0257/)
    - include concise descriptions of behavior with 
      [doctest](https://docs.python.org/3/library/doctest.html) examples
      -- make sure those doctests are run with the test suite by (TODO)
- ... (TODO)
