import doctest

import shtrove.util.chainmap
import shtrove.util.frozen
import shtrove.util.iris
import shtrove.util.iter
import shtrove.util.propertypath
import shtrove.vocab.mediatypes

_DOCTEST_OPTIONFLAGS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE

_MODULES_WITH_DOCTESTS = (
    shtrove.util.chainmap,
    shtrove.util.frozen,
    shtrove.util.iris,
    shtrove.util.iter,
    shtrove.util.propertypath,
    shtrove.vocab.mediatypes,
)


def load_tests(loader, tests, ignore):
    for _module in _MODULES_WITH_DOCTESTS:
        tests.addTests(doctest.DocTestSuite(_module, optionflags=_DOCTEST_OPTIONFLAGS))
    return tests
