"""shtrove.index.proto: interface for indexing metadata records for easy searching
"""
import collections.abc as cabc
import typing

from shtrove.proto import (
    ProtoCatalogRecord,
    ProtoCombinedMetadata,
)
from shtrove.util.propertypath import Propertypath


class ProtoIndexStrategy(typing.Protocol):
    def add_record(self, record: ProtoCatalogRecord, metadata: ProtoCombinedMetadata) -> None: ...
    def remove_record(self, record: ProtoCatalogRecord) -> None: ...
    def handle_recordsearch(self, recordsearch_args: ProtoRecordsearchArgs) -> ProtoRecordsearchHandle: ...
    def handle_valuesearch(self, valuesearch_args: ProtoValuesearchArgs) -> ProtoValuesearchHandle: ...


###
# args

class ProtoRecordsearchArgs(typing.Protocol):
    ...


class ProtoValuesearchArgs(typing.Protocol):
    ...


###
# response handles

class ProtoResponseHandle(typing.Protocol):
    cursor: ProtoPageCursor

    def __next__(self) -> typing.Self:
        raise StopIteration


class ProtoRecordsearchHandle(ProtoResponseHandle, typing.Protocol):
    recordsearch_args: ProtoRecordsearchArgs
    total_match_count: rdf.Literal
    match_sample: cabc.Iterable[ProtoRecordsearchMatch]
    suggested_paths: cabc.Iterable[PropertypathUsage]



class ProtoValuesearchHandle(ProtoResponseHandle, typing.Protocol):
    recordsearch_args: ProtoRecordsearchArgs
    valuesearch_args: ProtoValuesearchArgs
    total_match_count: rdf.Literal
    match_sample: cabc.Iterable[ProtoValuesearchIriMatch | ProtoValuesearchDateMatch]


class ProtoRecordsearchMatch(typing.Protocol):
    record_uuid: str
    text_match_evidence: cabc.Iterable[ProtoTextMatchEvidence]


class ProtoTextMatchEvidence(typing.Protocol):
    record_uuid: uuid.UUID
    path: Propertypath
    matching_highlight: rdf.Literal


class ProtoValuesearchIriMatch(typing.Protocol):
    value_iri: str
    value_type_iris: cabc.Iterable[str]
    title: rdf.Literal
    description: rdf.Literal
    record_count: rdf.Literal


class ProtoValuesearchDateMatch(typing.Protocol):
    date_value: rdf.Literal
    record_count: rdf.Literal


class ProtoPropertypathUsage:
    path: PropertyPath
    usage_count: rdf.Literal
