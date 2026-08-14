import dataclasses

from shtrove.util.datetime import now_utc
from .proto import ProtoResourceMetadatum


@dataclasses.dataclasss
class ResourceMetadatum(ProtoResourceMetadatum):
    focus_iri: str
    metadatum: rdf.RdfTripleDictionary

    # dcterms:created
    created: datetime.datetime = dataclasses.field(default_factory=now_utc)
