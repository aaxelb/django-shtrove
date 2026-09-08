"""shtrove.types.derive: interface for deriving a specific representation of a metadata record"""

from __future__ import annotations
import datetime
import typing

from primitive_metadata import primitive_rdf as rdf

from shtrove.types.record import ProtoCombinedMetadata


@typing.runtime_checkable
class ProtoDerive(typing.Protocol):
    def derive(
        self, upstream_metadata: ProtoCombinedMetadata
    ) -> ProtoDerivedMetadatum: ...


class ProtoDerivedMetadatum(typing.Protocol):
    focus_iri: str
    datatype_iri: str
    derived_metadatum: rdf.Literal

    # dcterms:created
    created: datetime.datetime
