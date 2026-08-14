
@dataclasses.dataclass
class BasicShtroveStrategy(ProtoShtroveStrategy):
    extract_strategies: cabc.Iterable[str] = (
        # TODO: 'shtrove.extract.basic.TurtleExtractStrategy',
        # TODO: 'shtrove.extract.basic.JsonldExtractStrategy',
    )
    persist_strategy: str = 'shtrove.persist.basic.TurtleExtractStrategy'
    derive_strategies: cabc.Iterable[str] = (
        # TODO: 'shtrove.derive.basic.OaidcDeriveStrategy'
    )
    index_strategies: cabc.Iterable[str] = ()
    render_strategies: cabc.Iterable[str] = (
        # TODO: 'shtrove.render.basic.HtmlRenderStrategy',
        # TODO: 'shtrove.render.basic.TurtleRenderStrategy',
        # TODO: 'shtrove.render.basic.JsonldRenderStrategy',
    )

    def way_to_extract(self, mediatype: str) -> ProtoExtractStrategy:
        # TODO: from entrypoints
        return ...

    def way_to_persist(self) -> ProtoPersistStrategy:
        # TODO: from entrypoints
        return ...

    def each_way_to_derive(self) -> cabc.Iterator[ProtoDeriveStrategy]:
        # TODO: from entrypoints
        return ...

    def each_way_to_index(self) -> cabc.Iterator[ProtoIndexStrategy]:
        # TODO: from entrypoints
        return ...

    def way_to_render(self, accepting: cabc.Sequence[str] = ()) -> ProtoRenderStrategy:
        # TODO: from entrypoints
        return ...

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
        _metadatum = shtrove.way_to_extract(input_mediatype).extract(
            input_document,
            focus_iri=focus_iri,
        )
        # persist
        _record = shtrove.way_to_persist().store_metadatum(_metadatum)
        # derive
        _combined_metadata = shtrove.way_to_persist().get_combined_metadata(_record.focus_iri)
        for _derive_strat in shtrove.each_way_to_derive():
            _derived_metadatum = _derive_strat.derive(_combined_metadata)
            if _derived_metadatum is not None:
                _persist_strat.store_derived_metadatum(derived_metadatum)
        # index
        for _index_strat in shtrove.each_way_to_index():
            _index_strat.set_item_metadata(_combined_metadata)
        return _record
