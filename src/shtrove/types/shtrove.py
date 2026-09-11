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
    ProtoGatheredResponse,
    ProtoPageCursor,
)


class ProtoShtrove(typing.Protocol):
    ###
    # getting imp(lamentation)s of various shtrove protocols

    def get_shtrove_extract_imp(self, mediatype: str) -> ProtoExtract: ...
    def get_shtrove_persist_imp(self) -> ProtoPersist: ...
    def each_shtrove_derive_imp(self) -> _abc.Iterable[ProtoDerive]: ...
    def each_shtrove_index_imp(self) -> _abc.Iterable[ProtoIndex]: ...
    def get_shtrove_search_imp(self, imp_name: str = "") -> ProtoIndex: ...
    def get_shtrove_render_imp(self, accepts: _abc.Sequence[str] = ()) -> ProtoRender: ...

    def shtrove_ingest(self, **kwargs) -> ProtoGatheredResponse: ...
    def shtrove_expel(self, **kwargs) -> ProtoGatheredResponse: ...

    def shtrove_record_search(
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
