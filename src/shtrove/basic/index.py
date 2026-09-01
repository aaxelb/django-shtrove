import collections.abc as _abc
import dataclasses

from shtrove.basic.checksum import Checksum
from shtrove.types.index import (
    ProtoIndexStatus,
    ProtoSubindexStatus,
)


@dataclasses.dataclass
class IndexStatus(ProtoIndexStatus):
    local_name: str
    config_checksum: Checksum
    is_set_up: bool

    def each_subindex_status(self) -> _abc.Iterable[ProtoSubindexStatus]: ...

    def each_existing_prior_index(self) -> _abc.Iterable[ProtoIndexStatus]: ...


@dataclasses.dataclass
class SubindexStatus(ProtoSubindexStatus):
    local_id: str
    creation_date: str | None = None
    record_count: int | None = None
