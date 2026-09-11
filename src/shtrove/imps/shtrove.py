import collections.abc as _abc
import functools

import shtrove.types as _types
from shtrove.util.entry_points import load_each_entry_point


class BasicShtrove(_types.ProtoShtrove):
    ###
    # for ProtoShtrove

    def get_shtrove_extract_imp(self, mediatype: str) -> _types.ProtoExtract:
        # TODO: better handle errors, init args, mediatype collisions
        return next(
            _extract_type()
            for _extract_type in self._each_extract_type()
            if _extract_type.accepts(mediatype)
        )

    def get_shtrove_persist_imp(self) -> _types.ProtoPersist:
        # TODO: basic persist (without database) -- write to files?
        raise NotImplementedError("no basic persist exists")

    def each_shtrove_derive_imp(self) -> _abc.Iterator[_types.ProtoDerive]:
        # TODO: handle errors, init args
        for _derive_type in self._each_derive_type():
            yield _derive_type()

    def each_index_imp(self) -> _abc.Iterator[_types.ProtoIndex]:
        # TODO: basic index (without elasticsearch)?
        raise NotImplementedError("no basic index exists")

    def get_shtrove_search_imp(self, name: str = "") -> _types.ProtoIndex:
        # TODO: basic index (without elasticsearch)?
        raise NotImplementedError("no basic search index exists")

    def way_to_render(self, accepts: _abc.Sequence[str] = ()) -> _types.ProtoRender:
        # TODO: better handle errors, init args, mediatype params, `Accept` header semantics...
        return next(
            self._render_types_by_mediatype[_mediatype]()
            for _mediatype in accepts
            if _mediatype in self._render_types_by_mediatype
        )

    ###
    # loading entrypoints
    # (TODO: should these be cached? is accessing package metadata slow?)

    def _each_extract_type(self) -> _abc.Iterable[type[_types.ProtoExtract]]:
        for _cls in load_each_entry_point("shtrove.ProtoExtract"):
            assert issubclass(_cls, _types.ProtoExtract)
            yield _cls

    def _each_derive_type(self) -> _abc.Iterable[type[_types.ProtoDerive]]:
        for _cls in load_each_entry_point("shtrove.ProtoDerive"):
            assert issubclass(_cls, _types.ProtoDerive)
            yield _cls

    def _each_render_type(self) -> _abc.Iterable[type[_types.ProtoRender]]:
        for _cls in load_each_entry_point("shtrove.ProtoRender"):
            assert issubclass(_cls, _types.ProtoRender)
            yield _cls

    @functools.cached_property
    def _render_types_by_mediatype(
        self,
    ) -> _abc.Mapping[str, type[_types.ProtoRender]]:
        _by_mediatype = {}
        for _render_type in self._each_render_type():
            _mediatype = _render_type.mediatype()
            if _mediatype in _by_mediatype:
                raise NotImplementedError(
                    "need to choose from multiple render strategies for a mediatype",
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
        record_identifier: str = "",  # default focus_iri
        is_supplementary: bool = False,
        # TODO: expiration_date: datetime.date | None = None,  # default "never"
        restore_deleted: bool = False,
        urgent: bool = False,
    ) -> _types.ProtoCatalogRecord:
        """ingest: extract + derive + persist + index"""
        # extract
        _metadatum = self.get_shtrove_extract_imp(input_mediatype).extract(
            input_document,
            focus_iri=focus_iri,
        )
        # persist
        if is_supplementary:
            _record = self.get_shtrove_persist_imp().store_supplementary_metadatum(
                _metadatum,
                supplement_identifier=record_identifier or focus_iri,
            )
        else:
            _record = self.get_shtrove_persist_imp().store_metadatum(
                _metadatum,
                record_identifier=record_identifier or focus_iri,
                restore_deleted=restore_deleted,
            )
        # derive
        _combined_metadata = self.get_shtrove_persist_imp().get_combined_metadata(
            *_record.focus_iris
        )
        for _derive in self.each_shtrove_derive_imp():
            _derived_metadatum = _derive.derive(_combined_metadata)
            if _derived_metadatum is not None:
                self.get_shtrove_persist_imp().store_derived_metadatum(
                    _derived_metadatum, record=_record
                )
        # index
        for _index in self.each_index_imp():
            _index.set_metadatum(_combined_metadata)
        return _record
