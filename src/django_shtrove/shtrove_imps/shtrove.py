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
        _kwargs, _entrypoint_name = self._get_instance_setting(
            settings.SHTROVE_PERSIST,
            "PERSIST_ENTRYPOINT",
        )
        _persist_constructor = load_entry_point(
            "shtrove.ProtoPersist",
            _entrypoint_name,
            ProtoPersist,
        )
        return _persist_constructor(**_kwargs)

    def each_way_to_index(self) -> _abc.Iterator[ProtoIndex]:
        """get a shtrove index instances from django setting `SHTROVE_INDEXES`"""
        for _index_name, _index_settings in settings.SHTROVE_INDEXES.items():
            _index_kwargs, _entrypoint_name = self._get_instance_setting(
                _index_settings,
                "INDEX_ENTRYPOINT",
            )
            _index_constructor = load_entry_point(
                "shtrove.ProtoIndex", _entrypoint_name, ProtoIndex
            )
            yield _index_constructor(**_index_kwargs)

    def way_to_search(self, name: str = "") -> ProtoIndex:
        # TODO: error handling
        return self._shtrove_index_from_setting(
            settings.SHTROVE_INDEXES[name]
            if name
            else next(settings.SHTROVE_INDEXES.values())
        )

    def _shtrove_index_from_setting(self, settings_dict: dict) -> ProtoIndex:
        _way = self._instance_from_setting(
            settings_dict,
            entrypoint_key="INDEX_ENTRYPOINT",
            entrypoint_group="shtrove.ProtoIndex",
        )
        assert isinstance(_way, ProtoIndex)
        return _way

    def _instance_from_setting(
        self,
        settings_dict: dict,
        entrypoint_key: str,
        entrypoint_group: str,
    ) -> object:
        _kwargs, _entrypoint_name = self._get_instance_setting(
            settings_dict, entrypoint_key
        )
        return load_entry_point(entrypoint_group, _entrypoint_name)(**_kwargs)

    def _get_instance_setting(
        self, settings_dict: dict[typing.Any, typing.Any], entrypoint_key: str
    ) -> tuple[dict[typing.Any, typing.Any], str]:
        _kwargs = {**settings_dict}
        _entrypoint_name = _kwargs.pop(entrypoint_key)
        return _kwargs, _entrypoint_name
