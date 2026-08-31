"""shtrove.types: interfaces for shtrove args and returns"""

from __future__ import annotations
import collections.abc as _abc
import typing
import uuid

from primitive_metadata import gather

from shtrove.extract.types import ProtoExtract
from shtrove.persist.types import ProtoPersist, ProtoCatalogRecord
from shtrove.derive.types import ProtoDerive
from shtrove.index.types import ProtoIndex
from shtrove.render.types import ProtoRender


class ProtoShtrove(typing.Protocol):
    def way_to_extract(self, mediatype: str) -> ProtoExtract: ...
    def each_way_to_persist(self) -> _abc.Iterator[ProtoPersist]: ...
    def each_way_to_derive(self) -> _abc.Iterator[ProtoDerive]: ...
    def each_way_to_index(self) -> _abc.Iterator[ProtoIndex]: ...
    def way_to_search(self, name: str = "") -> ProtoIndex: ...
    def way_to_render(self, accepts: _abc.Sequence[str] = ()) -> ProtoRender: ...

    def ingest(self, **kwargs) -> ProtoIngestResponse: ...
    def expel(self, **kwargs) -> ProtoExpelResponse: ...

    def search_records(self, **kwargs) -> ProtoGatheredResponse: ...
    def search_values(self, **kwargs) -> ProtoGatheredResponse: ...
    def browse_record(self, iri: str, **kwargs) -> ProtoGatheredResponse: ...


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
