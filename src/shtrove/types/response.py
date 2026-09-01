"""shtrove.types: interfaces for shtrove args and returns"""

from __future__ import annotations

__all__ = (
    "ProtoExpelResponse",
    "ProtoGatheredResponse",
    "ProtoIngestResponse",
    "ProtoPagedResponse",
    "ProtoPageCursor",
)

import collections.abc as _abc
import typing
import uuid

from primitive_metadata import gather

from shtrove.types.record import ProtoCatalogRecord

###
# response types


class ProtoIngestResponse(typing.Protocol):
    catalog_record: ProtoCatalogRecord


class ProtoExpelResponse(typing.Protocol):
    catalog_record_uuids: _abc.Collection[uuid.UUID]


class ProtoGatheredResponse(typing.Protocol):
    @property
    def focus(self) -> gather.Focus: ...

    @property
    def gathering(self) -> gather.Gathering: ...


class ProtoPagedResponse[T](typing.Protocol):
    items: _abc.Sequence[T]
    cursor: ProtoPageCursor

    def __next__(self) -> typing.Self:
        raise StopIteration


class ProtoPageCursor(typing.Protocol):
    @classmethod
    def from_str(cls, cursor_value: str) -> typing.Self:
        """deserialize a cursor from a string (perhaps from a a url query param)

        inverse of `__str__` instance method
        """

    def __str__(self) -> str:
        """serialize this cursor to a string (perhaps for use in a url query param)

        inverse of `from_str` class method
        """

    @property
    def page_size(self) -> int:
        """number of items on each page (approximately)

        should be >= 0
        """

    @property
    def total_count(self) -> int | float:
        """total number of items across all pages (approximately)

        for large counts, greater than 10000 or so, may return `math.inf`
        """

    def next_cursor(self) -> ProtoPageCursor | None: ...
    def prev_cursor(self) -> ProtoPageCursor | None: ...
    def first_cursor(self) -> ProtoPageCursor | None: ...
