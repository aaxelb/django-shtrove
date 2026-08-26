"""shtrove.index.types: interface for indexing metadata records for easy searching"""

from __future__ import annotations

import collections.abc as _abc
import typing
import uuid

from primitive_metadata import primitive_rdf as rdf

from shtrove.persist.types import (
    ProtoCatalogRecord,
    ProtoCombinedMetadata,
)
from shtrove.util.propertypath import Propertypath

__all__ = (
    "ProtoIndex",
    "ProtoRecordsearchArgs",
    "ProtoRecordsearchHandle",
    "ProtoValuesearchArgs",
    "ProtoValuesearchHandle",
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
    ) -> ProtoRecordsearchHandle: ...

    def handle_valuesearch(
        self, valuesearch_args: ProtoValuesearchArgs
    ) -> ProtoValuesearchHandle: ...


###
# search args


class ProtoRecordsearchArgs(typing.Protocol): ...  # TODO


class ProtoValuesearchArgs(typing.Protocol): ...  # TODO


class ProtoValuesearchHandle(ProtoResponseHandle, typing.Protocol):
    recordsearch_args: ProtoRecordsearchArgs
    valuesearch_args: ProtoValuesearchArgs
    total_match_count: rdf.Literal
    match_sample: _abc.Iterable[ProtoValuesearchIriMatch | ProtoValuesearchDateMatch]


class ProtoRecordsearchMatch(typing.Protocol):
    record_uuid: str
    text_match_evidence: _abc.Iterable[ProtoTextMatchEvidence]


class ProtoRecordsearchHandle(typing.Protocol, ProtoPagedResult[ProtoRecordsearchMatch]):
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
    path: PropertyPath
    usage_count: rdf.Literal
