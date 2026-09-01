"""shtrove.types: interfaces for shtrove args and returns"""

from __future__ import annotations

__all__ = ("ProtoShtrove",)

import collections.abc as _abc
import typing

from shtrove.types.derive import ProtoDerive
from shtrove.types.extract import ProtoExtract
from shtrove.types.index import ProtoIndex
from shtrove.types.persist import ProtoPersist
from shtrove.types.render import ProtoRender
from shtrove.types.response import (
    ProtoIngestResponse,
    ProtoExpelResponse,
    ProtoGatheredResponse,
    ProtoPageCursor,
)


class ProtoShtrove(typing.Protocol):
    def way_to_extract(self, mediatype: str) -> ProtoExtract: ...
    def each_way_to_persist(self) -> _abc.Iterator[ProtoPersist]: ...
    def each_way_to_derive(self) -> _abc.Iterator[ProtoDerive]: ...
    def each_way_to_index(self) -> _abc.Iterator[ProtoIndex]: ...
    def way_to_search(self, name: str = "") -> ProtoIndex: ...
    def way_to_render(self, accepts: _abc.Sequence[str] = ()) -> ProtoRender: ...

    def ingest(self, **kwargs) -> ProtoIngestResponse: ...
    def expel(self, **kwargs) -> ProtoExpelResponse: ...

    def search_records(
        self,
        *,
        cursor: ProtoPageCursor | None = None,
        **kwargs,
    ) -> ProtoGatheredResponse: ...

    def search_values(
        self,
        *,
        cursor: ProtoPageCursor | None = None,
        **kwargs,
    ) -> ProtoGatheredResponse: ...
    def browse_record(self, iri: str, **kwargs) -> ProtoGatheredResponse: ...
