"""utilities for file input/output"""

import collections.abc as _abc

__all__ = ("stream_file",)


def stream_file(filename: str) -> _abc.Iterator[str]:
    """open and read a file line by line, then close it when done

    be sure to iterate the whole thing!
    """
    with open(filename) as _f:
        yield from _f  # lines
