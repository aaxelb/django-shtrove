"""shtrove.derive.proto: interface for deriving a specific representation of a metadata record
"""
import typing

from primitive_metadata import primitive_rdf as rdf

from shtrove.proto import (
    ProtoResourceMetadatum,
    ProtoCatalogRecord,
    ProtoCombinedMetadata,
)


class ProtoPersistStrategy(typing.Protocol):
    ###
    # ingest

    def store_metadatum(self, resource_metadatum: ProtoResourceMetadatum) -> ProtoCatalogRecord: ...

    ###
    # browse by record uuid

    def get_record(self, record_uuid: uuid.UUID) -> ProtoCatalogRecord: ...
    def get_current_metadatum(self, record_uuid: uuid.UUID) -> ProtoResourceMetadatum: ...
    def get_each_supplementary_metadatum(self, record_uuid: uuid.UUID) -> cabc.Iterable[ProtoResourceMetadatum]: ...
    def get_each_archived_metadatum(self, record_uuid: uuid.UUID) -> cabc.Iterable[ProtoResourceMetadatum]: ...
    # TODO: consider optimized methods?
    # query/sort archived metadata by date?

    ###
    # browse by focus iri

    def get_metadata(self, focus_iri: str) -> ProtoCombinedMetadata: ...
    def get_each_record_by_focus(self, focus_iri: str) -> cabc.Iterable[ProtoCatalogRecord]: ...
