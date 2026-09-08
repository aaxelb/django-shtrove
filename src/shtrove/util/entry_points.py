__all__ = (
    "load_entry_point",
    "load_each_entry_point",
)

import collections.abc as _abc
import importlib.metadata
import typing

_T = typing.TypeVar("_T", bound=type)


def load_entry_point(group: str, name: str) -> typing.Any:
    (_ep,) = importlib.metadata.entry_points(group=group, name=name)
    return _ep.load()


def load_each_entry_point(group: str) -> _abc.Iterable[typing.Any]:
    for _ep in importlib.metadata.entry_points(group=group):
        yield _ep.load()
