"""shtrove.types.derive: interface for deriving a specific representation of a metadata record"""

from __future__ import annotations

__all__ = ("ProtoPersist",)

import collections.abc as cabc
import typing
import uuid

from shtrove.types.derive import ProtoDerivedMetadatum
from shtrove.types.extract import ProtoResourceMetadatum
from shtrove.types.record import (
    ProtoCatalogRecord,
    ProtoCombinedMetadata,
)


@typing.runtime_checkable
class ProtoPersist(typing.Protocol):
    ###
    # ingest

    def store_metadatum(
        self,
        resource_metadatum: ProtoResourceMetadatum,
        *,
        record_identifier: str = "",
        restore_deleted: bool = False,
    ) -> ProtoCatalogRecord: ...

    def store_supplementary_metadatum(
        self,
        resource_metadatum: ProtoResourceMetadatum,
        *,
        supplement_identifier: str,
    ) -> ProtoCatalogRecord: ...

    def store_derived_metadatum(
        self,
        derived_metadatum: ProtoDerivedMetadatum,
        *,
        record: ProtoCatalogRecord,
    ) -> None: ...

    ###
    # browse by record uuid

    def get_record(self, record_uuid: uuid.UUID) -> ProtoCatalogRecord: ...

    def get_current_metadatum(
        self, record_uuid: uuid.UUID
    ) -> ProtoResourceMetadatum: ...

    def get_each_supplementary_metadatum(
        self, record_uuid: uuid.UUID
    ) -> cabc.Iterable[ProtoResourceMetadatum]: ...

    def get_each_archived_metadatum(
        self, record_uuid: uuid.UUID
    ) -> cabc.Iterable[ProtoResourceMetadatum]: ...

    def get_derived_metadatum(
        self, record_uuid: uuid.UUID, derived_datatype_iri: str
    ) -> ProtoDerivedMetadatum: ...

    # TODO: consider optimized methods?
    # query/sort archived metadata by date?

    ###
    # browse by focus iri

    def get_combined_metadata(self, focus_iri: str) -> ProtoCombinedMetadata: ...

    def get_each_record_by_focus(
        self, focus_iri: str
    ) -> cabc.Iterable[ProtoCatalogRecord]: ...
