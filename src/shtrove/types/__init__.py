"""shtrove.types: interfaces for shtrove args and returns"""

__all__ = (
    "ProtoCatalogRecord",
    "ProtoDerive",
    "ProtoExpelResponse",
    "ProtoExtract",
    "ProtoGatheredResponse",
    "ProtoIndex",
    "ProtoIngestResponse",
    "ProtoPageCursor",
    "ProtoPagedResponse",
    "ProtoPersist",
    "ProtoRender",
    "ProtoShtrove",
)

from shtrove.types.extract import ProtoExtract
from shtrove.types.persist import ProtoPersist
from shtrove.types.response import (
    ProtoExpelResponse,
    ProtoGatheredResponse,
    ProtoIngestResponse,
    ProtoPageCursor,
    ProtoPagedResponse,
)
from shtrove.types.record import ProtoCatalogRecord
from shtrove.types.derive import ProtoDerive
from shtrove.types.index import ProtoIndex
from shtrove.types.render import ProtoRender
