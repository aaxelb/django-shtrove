"""shtrove.derive.proto: interface for deriving a specific representation of a metadata record
"""
import typing

from primitive_metadata import primitive_rdf as rdf

from shtrove.proto import ProtoCombinedMetadata


class ProtoDeriveStrategy(typing.Protocol):
    def derive(self, upstream_metadata: cabc.Iterable[ProtoCombinedMetadata]) -> rdf.Literal: ...
