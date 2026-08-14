"""shtrove.persist.basic: simple implementations of shtrove.persist interfaces
"""
import collections.abc as cabc
import dataclasses
import uuid

from primitive_metadata import primitive_rdf as rdf

from .proto import (
    ProtoCatalogRecord,
    ProtoCombinedMetadata,
    ProtoResourceMetadatum,
    ProtoPersistStrategy,
)


class EphemeralPersist(ProtoPersistStrategy):
    ...  # TODO


@dataclasses.dataclass(kw_only=True)
class CatalogRecord(ProtoCatalogRecord):
    """CatalogRecord: describing a shtrove catalog record

    corresponds to `dcat:CatalogRecord`: https://www.w3.org/TR/vocab-dcat/#Class:Catalog_Record
    """
    record_uuid: uuid.UUID

    # foaf:primaryTopic (iris synonymously identifying a single resource, owl:sameAs each other)
    focus_iris: cabc.Iterable[str]

    # foaf:primaryTopic / rdfs:type
    focustype_iris: cabc.Iterable[str] = ()

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
    each_supplementary_metadatum: cabc.Iterable[ProtoResourceMetadatum] = ()


@dataclasses.dataclass
class CombinedMetadata(ProtoCombinedMetadata):
    focus_iri: str
    each_record: cabc.Iterable[ProtoCatalogRecord]
