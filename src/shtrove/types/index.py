"""shtrove.types.index: interface for indexing metadata records for easy searching"""

from __future__ import annotations

import collections.abc as _abc
import typing
import uuid

from primitive_metadata import primitive_rdf as rdf

from shtrove.types.checksum import ProtoChecksum
from shtrove.types.record import ProtoCombinedMetadata
from shtrove.types.response import (
    ProtoPagedResponse,
    ProtoPageCursor,
)
from shtrove.util.propertypath import Propertypath

__all__ = (
    "ProtoIndex",
    "ProtoIndexStatus",
    "ProtoRecordsearchArgs",
    "ProtoRecordsearchResponse",
    "ProtoValuesearchArgs",
    "ProtoValuesearchResponse",
)


@typing.runtime_checkable
class ProtoIndex(typing.Protocol):
    ###
    # index lifecycle
    def do_initial_setup(self) -> None: ...
    def do_update_setup(self) -> None: ...
    def do_teardown(self, *, really_really: bool) -> None: ...
    def get_index_status(self) -> ProtoIndexStatus: ...

    ###
    # adding/updating/removing metadata
    def set_item_metadata(self, metadata: ProtoCombinedMetadata) -> None: ...

    ###
    # searching
    def handle_recordsearch(
        self, recordsearch_args: ProtoRecordsearchArgs
    ) -> ProtoRecordsearchResponse: ...

    def handle_valuesearch(
        self, valuesearch_args: ProtoValuesearchArgs
    ) -> ProtoValuesearchResponse: ...


###
# index status


class ProtoIndexStatus(typing.Protocol):
    @property
    def local_name(self) -> str: ...
    @property
    def config_checksum(self) -> ProtoChecksum: ...
    @property
    def is_set_up(self) -> bool: ...
    @property
    def each_subindex_status(self) -> _abc.Iterable[ProtoSubindexStatus]: ...
    @property
    def each_existing_prior_index(self) -> _abc.Iterable[ProtoIndexStatus]: ...


class ProtoSubindexStatus(typing.Protocol):
    @property
    def local_id(self) -> str: ...
    @property
    def creation_date(self) -> str | None: ...
    @property
    def record_count(self) -> int | None: ...


###
# search args


class ProtoRecordsearchArgs(typing.Protocol):
    ...  # TODO

    @property
    def cursor(self) -> ProtoPageCursor | None: ...


class ProtoValuesearchArgs(typing.Protocol):
    ...  # TODO

    @property
    def cursor(self) -> ProtoPageCursor | None: ...


type ProtoValuesearchMatch = ProtoValuesearchIriMatch | ProtoValuesearchDateMatch


class ProtoValuesearchResponse(
    ProtoPagedResponse[ProtoValuesearchMatch],
    typing.Protocol,
):
    recordsearch_args: ProtoRecordsearchArgs
    valuesearch_args: ProtoValuesearchArgs
    total_match_count: rdf.Literal
    items: _abc.Sequence[ProtoValuesearchMatch]  # inherited from ProtoPagedResponse


class ProtoRecordsearchMatch(typing.Protocol):
    record_uuid: str
    text_match_evidence: _abc.Iterable[ProtoTextMatchEvidence]


class ProtoRecordsearchResponse(
    ProtoPagedResponse[ProtoRecordsearchMatch],
    typing.Protocol,
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
