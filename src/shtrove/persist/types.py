"""shtrove.derive.types: interface for deriving a specific representation of a metadata record"""

from __future__ import annotations

__all__ = (
    "ProtoCatalogRecord",
    "ProtoPersist",
    "ProtoCombinedMetadata",
)

import collections.abc as cabc
import datetime
import typing
import uuid

from primitive_metadata import primitive_rdf as rdf

from shtrove.derive.types import ProtoDerivedMetadatum
from shtrove.extract.types import ProtoResourceMetadatum


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
        self, derived_metadatum: ProtoDerivedMetadatum, *, record
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


class ProtoCatalogRecord(typing.Protocol):
    """ProtoCatalogRecord: describing a shtrove catalog record

    corresponds to `dcat:CatalogRecord`: https://www.w3.org/TR/vocab-dcat/#Class:Catalog_Record
    """

    record_uuid: uuid.UUID

    # foaf:primaryTopic (iris synonymously identifying a single resource, owl:sameAs each other)
    focus_iris: cabc.Iterable[str]

    # foaf:primaryTopic >> rdfs:type
    focustype_iris: cabc.Iterable[str]

    # dcterms:title
    record_title: rdf.Literal

    # dcterms:description
    record_description: rdf.Literal

    # dcterms:issued
    issued: datetime.datetime

    # dcterms:modified
    modified: datetime.datetime

    # shtrove-specific relationships
    each_current_metadatum: cabc.Iterable[ProtoResourceMetadatum]
    each_supplementary_metadatum: cabc.Iterable[ProtoResourceMetadatum]


class ProtoCombinedMetadata(typing.Protocol):
    focus_iri: str
    each_record: cabc.Iterable[ProtoCatalogRecord]
