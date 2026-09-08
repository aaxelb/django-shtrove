import doctest

_DOCTEST_OPTIONFLAGS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE

_MODULES_WITH_DOCTESTS = (
    # django_shtrove. ...
)


def load_tests(loader, tests, ignore):
    for _module in _MODULES_WITH_DOCTESTS:
        tests.addTests(doctest.DocTestSuite(_module, optionflags=_DOCTEST_OPTIONFLAGS))
    return tests
