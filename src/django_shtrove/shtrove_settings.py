from django.conf import settings

from shtrove.basic import BasicShtroveStrategy


class DjangoShtroveStrategy(BasicShtroveStrategy):
    def way_to_persist(self) -> ProtoPersistStrategy:
        """get a shtrove persist instance from django setting `SHTROVE_PERSIST`"""
        # TODO: handle errors
        return _instance_from_setting(
            settings.SHTROVE_PERSIST,
            entrypoint_key="PERSIST_ENTRYPOINT",
            entrypoint_group="shtrove.persist",
        )

    def each_way_to_index(self) -> cabc.Iterator[ProtoIndexStrategy]:
        """get a shtrove index instances from django setting `SHTROVE_INDEXES`"""
        for _index_name, _index_kwargs in settings.SHTROVE_INDEXES.items():
            yield _instance_from_setting(
                _index_kwargs,
                entrypoint_key="INDEX_ENTRYPOINT",
                entrypoint_group="shtrove.index",
            )

    def way_to_search(self, name: str = "") -> ProtoIndexStrategy:
        for _index_name, _index_kwargs in settings.SHTROVE_INDEXES.items():
            yield _instance_from_setting(
                _index_kwargs,
                entrypoint_key="INDEX_ENTRYPOINT",
                entrypoint_group="shtrove.index",
            )


def _instance_from_setting(
    settings_dict: dict,
    entrypoint_key: str,
    entrypoint_group: str,
):
    _kwargs = {**settings_dict}
    _entrypoint_name = _kwargs.pop(entrypoint_key)
    return load_entry_point(entrypoint_group, _entrypoint_name)(**_kwargs)
