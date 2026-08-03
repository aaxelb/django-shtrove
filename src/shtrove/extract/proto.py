"""shtrove.extract.proto: abstract interface for extracting metadata from a type of document
"""
import typing

from shtrove.proto import ProtoResourceMetadatum


class ProtoExtractStrategy(typing.Protocol):
    def extract(self, input_document: str, *, focus_iri: str) -> ProtoResourceMetadatum: ...
