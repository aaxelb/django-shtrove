# django-shtrove TODO

see docstrings in `src/django_shtrove/**.py` for more plans/details

## yet to do
- django_shtrove migrations
- local dev setup (compose.yaml) **
- digestive_tract from SHARE
- index strategies from SHARE
- management commands from SHARE
- admin interface from SHARE
- views/gather/render from SHARE
- urls from SHARE
- django_shtrove settings
- testapp
- copy trove tests
- passing django_shtrove tests
- linting
- formatting
- ci
- thorough README
    - link to READMEs in subfolders -- organize code conceptually


## done
- initial project structure
- document initial plans in docstrings
- django scaffolding
- django_shtrove models from SHARE
- util from SHARE
- shtrove tests (non-django)
- entrypoints for strategies: extract, store, derive, render, index
- use entry-points to register/discover indexing strategy implementations
    - replace static share.search.index_strategy._AvailableStrategies
    - see https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/#using-package-metadata
