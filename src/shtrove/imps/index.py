import collections.abc as _abc
import dataclasses

from shtrove.imps.checksum import Checksum
from shtrove.types.index import (
    ProtoIndexStatus,
    ProtoSubindexStatus,
)


@dataclasses.dataclass
class ShtroveIndexStatus(ProtoIndexStatus):
    imp_name: str
    current_config_checksum: Checksum
    is_set_up: bool
    each_partindex_status: _abc.Iterable[ProtoSubindexStatus] = ()
    each_existing_prior_index: _abc.Iterable[ProtoIndexStatus] = ()


@dataclasses.dataclass
class ShtroveSubindexStatus(ProtoSubindexStatus):
    local_id: str
    creation_date: str | None = None
    record_count: int | None = None
