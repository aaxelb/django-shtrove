"""some helpful utilities for python typing"""

import collections.abc as _abc
import typing

_T = typing.TypeVar("_T")

type NoopDecorator[_T] = _abc.Callable[[_T], _T]


def implements(given_type: _T) -> NoopDecorator[_T]:
    """decorator to prompt static type-checking on an implementation of an abstract type

    does nothing at runtime -- like typing.assert_type, but as a decorator

    meant mainly to help implement a typing.Protocol without inheriting
    (say, to avoid property descriptor clashing with a dataclass field)
    while still keeping it near the start of the definition for clarity

    >>> @implements(_abc.Container)
    ... class AllContainer:
    ...     def __contains__(self, item):
    ...         return True  # contains all
    """
    def _decorator(given_obj: _T) -> _T:
        return given_obj
    return _decorator


if __debug__:  # for static checking only
    import dataclasses

    class _MyProto(typing.Protocol):
        foo: int

        @property
        def bar(self) -> int: ...

        def blarg(self) -> str: ...

    @implements(_MyProto)  # no type errors -- but would if type annotations were incompatible
    @dataclasses.dataclass
    class _MyContainer:
        foo: int
        bar: int

        def blarg(self) -> str:
            return 'blarg'
