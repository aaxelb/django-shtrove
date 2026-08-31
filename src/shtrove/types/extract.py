"""shtrove.types.extract: abstract interface for extracting metadata from a type of document"""

import collections.abc as cabc
import datetime
import typing

from primitive_metadata import primitive_rdf as rdf


class ProtoResourceMetadatum(typing.Protocol):
    focus_iri: str
    metadatum: rdf.RdfTripleDictionary

    # dcterms:created
    created: datetime.datetime


@typing.runtime_checkable
class ProtoExtract(typing.Protocol):
    @classmethod
    def accepts(cls, mediatype: str) -> bool: ...

    def extract(
        self, input_stream: cabc.Iterable[str], *, focus_iri: str
    ) -> ProtoResourceMetadatum: ...
