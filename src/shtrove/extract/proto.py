"""shtrove.extract.proto: abstract interface for extracting metadata from a type of document
"""
import typing


class ProtoExtractStrategy(typing.Protocol):
    @classmethod
    def accepts(cls, mediatype: str) -> bool: ...

    def extract(self, input_document: str, *, focus_iri: str) -> ProtoResourceMetadatum: ...


class ProtoResourceMetadatum(typing.Protocol):
    focus_iri: str
    metadatum: rdf.RdfTripleDictionary

    # dcterms:created
    created: datetime.datetime
