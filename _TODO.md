# django-shtrove TODO

see docstrings in `src/*/**.py` for more plans/details

## yet to do
- django_shtrove migrations
- local dev setup (compose.yaml) (partly)
- index strategies from SHARE (`TrovesearchDenormIndexStrategy` to `ShtrovesearchIndexES8(ProtoIndex)`)
- management commands from SHARE (`shtrove_index_setup`, `shtrove_index_teardown`)
- admin interface from SHARE/trove (shtrove models, index status/lifecycle)
- base views/responders from SHARE/trove
- search/browse gatherings from SHARE/trove
- render from SHARE/trove
- django_shtrove settings (define, document)
- django_shtrove urls
- testapp
- passing django_shtrove tests
- linting
- formatting
- ci
- thorough README and code docs
    - link to READMEs in subfolders -- organize code conceptually


## done
- basic README
- initial project structure
- document initial plans in docstrings
- django scaffolding
- django_shtrove models from SHARE
- util from SHARE
- shtrove tests (non-django)
- entrypoints for strategies: extract, store, derive, render, index
- use entry-points to register/discover indexing strategy imps
    - replace static share.search.index_strategy._AvailableStrategies
    - see https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/#using-package-metadata
- digestive_tract from SHARE (as BasicShtrove.ingest)
- copy trove tests
