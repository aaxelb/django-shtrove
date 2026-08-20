SECRET_KEY = "fake-key"
INSTALLED_APPS = [
    "django_shtrove",
]

SHTROVE_PERSIST = {
    'PERSIST_ENTRYPOINT': 'django_shtrove_persist',
}
SHTROVE_INDEXES = {
    'default': {
        'INDEX_ENTRYPOINT': 'shtrovesearch_elastic8',
        'hosts': ...,
    },
}
