__all__ = (
    "load_entry_point",
    "load_each_entry_point",
)

import collections.abc as _abc
import importlib.metadata
import typing

from shtrove import exceptions

_T = typing.TypeVar("_T", bound=type)


def load_entry_point(group: str, name: str, expect_type: _T) -> _T:
    (_ep,) = importlib.metadata.entry_points(group=group, name=name)
    return _load_ep(_ep, expect_type)


def load_each_entry_point(group: str, expect_type: _T) -> _abc.Iterator[_T]:
    for _ep in importlib.metadata.entry_points(group=group):
        yield _load_ep(_ep, expect_type)


def _load_ep(ep: importlib.metadata.EntryPoint, expect_type: _T) -> _T:
    _loaded = ep.load()
    if not issubclass(_loaded, expect_type):
        raise exceptions.BadEntryPoint(ep, expect_type, _loaded)
    return _loaded  # type: ignore[no-any-return]
