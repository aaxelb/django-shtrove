"""shtrove.derive.types: interface for deriving a specific representation of a metadata record"""

from __future__ import annotations
import collections.abc as _abc
import datetime
import typing

from primitive_metadata import primitive_rdf as rdf

from shtrove.persist.types import ProtoCombinedMetadata


class ProtoDerive(typing.Protocol):
    def derive(
        self, upstream_metadata: _abc.Iterable[ProtoCombinedMetadata]
    ) -> ProtoDerivedMetadatum: ...


class ProtoDerivedMetadatum(typing.Protocol):
    focus_iri: str
    datatype_iri: str
    derived_metadatum: rdf.Literal

    # dcterms:created
    created: datetime.datetime
