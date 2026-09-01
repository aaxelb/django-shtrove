"""shtrove.types.derive: interface for deriving a specific representation of a metadata record"""

from __future__ import annotations
import collections.abc as _abc
import datetime
import typing

from primitive_metadata import primitive_rdf as rdf

from shtrove.types.persist import ProtoCombinedMetadata


@typing.runtime_checkable
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
