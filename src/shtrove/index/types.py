"""shtrove.index.types: interface for indexing metadata records for easy searching"""

from __future__ import annotations

import collections.abc as _abc
import typing
import uuid

from primitive_metadata import primitive_rdf as rdf

from shtrove.persist.types import ProtoCombinedMetadata
from shtrove.types import ProtoPagedReturn
from shtrove.util.propertypath import Propertypath

__all__ = (
    "ProtoIndex",
    "ProtoRecordsearchArgs",
    "ProtoRecordsearchReturn",
    "ProtoValuesearchArgs",
    "ProtoValuesearchReturn",
)


class ProtoIndex(typing.Protocol):
    ###
    # index lifecycle
    def do_setup(self) -> None: ...
    def do_teardown(self) -> None: ...

    ###
    # adding/updating/removing metadata
    def set_item_metadata(self, metadata: ProtoCombinedMetadata) -> None: ...

    ###
    # searching
    def handle_recordsearch(
        self, recordsearch_args: ProtoRecordsearchArgs
    ) -> ProtoRecordsearchReturn: ...

    def handle_valuesearch(
        self, valuesearch_args: ProtoValuesearchArgs
    ) -> ProtoValuesearchReturn: ...


###
# search args


class ProtoRecordsearchArgs(typing.Protocol): ...  # TODO


class ProtoValuesearchArgs(typing.Protocol): ...  # TODO


type ProtoValuesearchMatch = ProtoValuesearchIriMatch | ProtoValuesearchDateMatch


class ProtoValuesearchReturn(ProtoPagedReturn[ProtoValuesearchMatch], typing.Protocol):
    recordsearch_args: ProtoRecordsearchArgs
    valuesearch_args: ProtoValuesearchArgs
    total_match_count: rdf.Literal
    items: _abc.Sequence[ProtoValuesearchMatch]  # inherited from ProtoPagedReturn


class ProtoRecordsearchMatch(typing.Protocol):
    record_uuid: str
    text_match_evidence: _abc.Iterable[ProtoTextMatchEvidence]


class ProtoRecordsearchReturn(
    ProtoPagedReturn[ProtoRecordsearchMatch], typing.Protocol
):
    recordsearch_args: ProtoRecordsearchArgs
    total_match_count: rdf.Literal
    match_sample: _abc.Iterable[ProtoRecordsearchMatch]
    # suggested_paths: _abc.Iterable[PropertypathUsage]


class ProtoTextMatchEvidence(typing.Protocol):
    record_uuid: uuid.UUID
    path: Propertypath
    matching_highlight: rdf.Literal


class ProtoValuesearchIriMatch(typing.Protocol):
    value_iri: str
    value_type_iris: _abc.Iterable[str]
    title: rdf.Literal
    description: rdf.Literal
    record_count: rdf.Literal


class ProtoValuesearchDateMatch(typing.Protocol):
    date_value: rdf.Literal
    record_count: rdf.Literal


class ProtoPropertypathUsage(typing.Protocol):
    path: Propertypath
    usage_count: rdf.Literal
