import collections.abc as _abc

from django.conf import settings

from shtrove.basic import BasicShtrove
from shtrove.types import (
    ProtoPersist,
    ProtoIndex,
)
from shtrove.util.entry_points import load_entry_point


class DjangoShtrove(BasicShtrove):
    def way_to_persist(self) -> ProtoPersist:
        """get a shtrove persist instance from django setting `SHTROVE_PERSIST`"""
        # TODO: handle errors
        return _instance_from_setting(
            settings.SHTROVE_PERSIST,
            entrypoint_key="PERSIST_ENTRYPOINT",
            entrypoint_group="shtrove.ProtoPersist",
        )

    def each_way_to_index(self) -> _abc.Iterator[ProtoIndex]:
        """get a shtrove index instances from django setting `SHTROVE_INDEXES`"""
        for _index_name, _index_kwargs in settings.SHTROVE_INDEXES.items():
            yield _instance_from_setting(
                _index_kwargs,
                entrypoint_key="INDEX_ENTRYPOINT",
                entrypoint_group="shtrove.ProtoIndex",
            )

    def way_to_search(self, name: str = "") -> ProtoIndex:
        # TODO: error handling
        _index_kwargs = (
            settings.SHTROVE_INDEXES[name]
            if name
            else next(settings.SHTROVE_INDEXES.values())
        )
        return _instance_from_setting(
            _index_kwargs,
            entrypoint_key="INDEX_ENTRYPOINT",
            entrypoint_group="shtrove.ProtoIndex",
        )


def _instance_from_setting(
    settings_dict: dict,
    entrypoint_key: str,
    entrypoint_group: str,
):
    _kwargs = {**settings_dict}
    _entrypoint_name = _kwargs.pop(entrypoint_key)
    return load_entry_point(entrypoint_group, _entrypoint_name)(**_kwargs)
