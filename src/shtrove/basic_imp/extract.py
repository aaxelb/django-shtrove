import dataclasses
import datetime

from primitive_metadata import primitive_rdf as rdf

from shtrove.util.datetime import now_utc
from .types import ProtoResourceMetadatum


@dataclasses.dataclass
class ResourceMetadatum(ProtoResourceMetadatum):
    focus_iri: str
    metadatum: rdf.RdfTripleDictionary

    # dcterms:created
    created: datetime.datetime = dataclasses.field(default_factory=now_utc)
