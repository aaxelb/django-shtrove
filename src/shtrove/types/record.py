"""shtrove.types.record: interface for deriving a specific representation of a metadata record"""

from __future__ import annotations

__all__ = (
    "ProtoCatalogRecord",
    "ProtoCombinedMetadata",
)

import collections.abc as cabc
import datetime
import typing
import uuid

from primitive_metadata import primitive_rdf as rdf

from shtrove.types.extract import ProtoResourceMetadatum


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
