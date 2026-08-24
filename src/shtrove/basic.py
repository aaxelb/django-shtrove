from shtrove.types import ProtoShtrove


@dataclasses.dataclass
class BasicShtrove(ProtoShtrove):
    ###
    # for ProtoShtrove

    def way_to_extract(self, mediatype: str) -> ProtoExtract:
        # TODO: better handle errors, init args, mediatype collisions
        return next(
            _extract_type()
            for _extract_type in self._each_extract_type()
            if _extract_type.accepts(mediatype)
        )

    def way_to_persist(self) -> ProtoPersist:
        # TODO: basic persist (without database) -- write to files?
        raise NotImplementedError('no basic persist exists')

    def each_way_to_derive(self) -> cabc.Iterator[ProtoDerive]:
        # TODO: handle errors, init args
        for _derive_type in self._each_derive_type():
            yield _derive_type()

    def each_way_to_index(self) -> cabc.Iterator[ProtoIndex]:
        # TODO: basic index (without elasticsearch)?
        raise NotImplementedError('no basic index exists')

    def way_to_search(self, name: str = '') -> ProtoIndex:
        # TODO: basic index (without elasticsearch)?
        raise NotImplementedError('no basic search index exists')

    def way_to_render(self, accepting: cabc.Sequence[str]) -> ProtoRender:
        # TODO: better handle errors, init args, mediatype params, `Accept` header semantics...
        return next(
            self._render_types_by_mediatype[_mediatype]()
            for _mediatype in accepting
            if _mediatype in self._render_types_by_mediatype
        )

    ###
    # loading entrypoints
    # (TODO: should these be cached? is accessing package metadata slow?)

    def _each_extract_type(self) -> cabc.Iterable[type[ProtoExtract]]:
        return load_each_entry_point('shtrove.extract')

    def _each_derive_type(self) -> cabc.Iterable[type[ProtoDerive]]:
        return load_each_entry_point('shtrove.derive')

    def _each_render_type(self) -> cabc.Sequence[type[ProtoRender]]:
        return load_each_entry_point('shtrove.render')

    @functools.cached_property
    def _render_types_by_mediatype(self) -> cabc.Mapping[str, type[ProtoRender]]:
        _by_mediatype = {}
        for _render_type in self._each_render_type():
            _mediatype = _render_type.mediatype()
            if _mediatype in _by_mediatype:
                raise NotImplementedError(
                    'need to choose from multiple render strategies for a mediatype',
                    _mediatype,
                )
            _by_mediatype[_mediatype] = _render_type
        return _by_mediatype

    ###
    # conveniences

    def ingest(
        self,
        *,  # all keyword-args
        focus_iri: str,
        input_mediatype: str,
        input_document: str,
        record_identifier: str | None = None,  # default focus_iri
        is_supplementary: bool = False,
        # TODO: expiration_date: datetime.date | None = None,  # default "never"
        restore_deleted: bool = False,
        urgent: bool = False,
    ) -> None:
        '''ingest: extract + derive + persist + index'''
        # extract
        _metadatum = self.way_to_extract(input_mediatype).extract(
            input_document,
            focus_iri=focus_iri,
        )
        # persist
        if is_supplementary:
            _record = self.way_to_persist().store_supplementary_metadatum(
                _metadatum,

            )
        _record = self.way_to_persist().store_metadatum(
            _metadatum,

        )
        # derive
        _combined_metadata = self.way_to_persist().get_combined_metadata(_record.focus_iri)
        for _derive_strat in self.each_way_to_derive():
            _derived_metadatum = _derive_strat.derive(_combined_metadata)
            if _derived_metadatum is not None:
                _persist_strat.store_derived_metadatum(derived_metadatum)
        # index
        for _index_strat in self.each_way_to_index():
            _index_strat.set_item_metadata(_combined_metadata)
        return _record
