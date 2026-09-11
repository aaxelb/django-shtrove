from __future__ import annotations
import abc
import collections.abc as _abc
import dataclasses
import functools
from http import HTTPStatus
import logging
import typing

from django.conf import settings
import elasticsearch8
from elasticsearch8.helpers import streaming_bulk

from shtrove import types as _types
from shtrove.imps.index import (
    ShtroveIndexStatus,
    ShtroveSubindexStatus,
)
from shtrove.imps.checksum import Checksum
from share.search.index_status import IndexStatus
from share.search import messages
from share.search.index_strategy._util import timestamp_to_readable_datetime
from ._indexnames import (
    parse_indexname_parts,
    combine_indexname_parts,
)

logger = logging.getLogger(__name__)


class _LocalIndexConfig(typing.TypedDict):
    local_name: str
    mappings: _types.json.JsonObject
    settings: _types.json.JsonObject


class ShareLegacyElastic8Imp(_types.ProtoIndex, abc.ABC):
    """abstract base class for index strategies using elasticsearch 8"""

    ###
    # abstract methods for subclasses to implement

    @classmethod
    @abc.abstractmethod
    def each_elastic_index_config(cls) -> _abc.Iterable[_LocalIndexConfig]:
        raise NotImplementedError

    @abc.abstractmethod
    def set_metadatum(self, metadata: _types.ProtoCombinedMetadata) -> None:
        raise NotImplementedError

    ###
    # methods for ProtoIndex

    def do_shtrove_index_setup(self) -> None:
        """for ProtoIndex"""
        for _local_name in self._local_indexes():
            self._ensure_elastic_index(_local_name)

    @abc.abstractmethod
    def do_shtrove_index_teardown(self, *, really_really: bool) -> None:
        """for ProtoIndex"""
        raise NotImplementedError

    def get_shtrove_index_status(self) -> _types.index.ProtoIndexStatus:
        """for ProtoIndex"""
        _partindex_statuses: list[_types.index.ProtoSubindexStatus] = []
        _prior_strategy_statuses: list[_types.index.ProtoIndexStatus] = []
        if self.is_current:
            _partindex_statuses = [
                _index.pls_get_status() for _index in self.each_partindex()
            ]
            _prior_strategies = {
                _index.index_strategy
                for _index in self.each_existing_index(any_strategy_check=True)
                if not _index.shtrove_index.is_current
            }
            _prior_strategy_statuses = [
                _strategy.pls_get_strategy_status() for _strategy in _prior_strategies
            ]
        else:
            _partindex_statuses = [
                _index.pls_get_status() for _index in self.each_existing_index()
            ]
        return ShtroveIndexStatus(
            strategy_name=self.strategy_name,
            strategy_check=self.strategy_check,
            is_set_up=self.pls_check_exists(),
            is_default_for_searching=(self == self.pls_get_default_for_searching()),
            index_statuses=_partindex_statuses,
            existing_prior_strategies=_prior_strategy_statuses,
        )

    ###
    # implementation for subclasses to mostly ignore

    @classmethod
    @functools.cache
    def _local_indexes(cls) -> _abc.Mapping[str, _LocalIndexConfig]:
        # readonly and cached per class
        return {
            _elastic_index_config["local_name"]: _elastic_index_config
            for _elastic_index_config in cls.each_elastic_index_config()
        }

    @classmethod
    def compute_current_config_checksum(cls) -> Checksum:
        return Checksum.digest_json(
            prefix=cls.__name__,
            raw_json=cls._local_indexes(),  # type: ignore[arg-type]
        )

    @classmethod
    def _each_local_name(self) -> typing.Iterable[str]:
        yield from self._local_indexes().keys()

    @classmethod
    @functools.cache
    def _get_elastic8_client(cls) -> elasticsearch8.Elasticsearch:
        should_sniff = settings.ELASTICSEARCH["SNIFF"]
        timeout = settings.ELASTICSEARCH["TIMEOUT"]
        return elasticsearch8.Elasticsearch(
            hosts=settings.ELASTICSEARCH8_URL,
            ssl_assert_hostname=settings.ELASTICSEARCH8_ASSERT_HOSTNAME,
            # security:
            ca_certs=settings.ELASTICSEARCH8_CERT_PATH,
            basic_auth=(
                (settings.ELASTICSEARCH8_USERNAME, settings.ELASTICSEARCH8_SECRET)
                if settings.ELASTICSEARCH8_SECRET is not None
                else None
            ),
            # retry:
            retry_on_timeout=True,
            request_timeout=timeout,
            # sniffing:
            sniff_on_start=should_sniff,
            sniff_before_requests=should_sniff,
            sniff_on_node_failure=should_sniff,
            sniff_timeout=timeout,
            min_delay_between_sniffing=timeout,
        )

    @property
    def es8_client(self):
        return self._get_elastic8_client()  # cached classmethod for shared client

    @property
    def _indexname_prefix_parts(self) -> list[str]:
        return [self.strategy_name, self.strategy_check]

    def _full_elastic_index_name(self, local_name: str) -> str:
        return combine_indexname_parts(
            *self._indexname_prefix_parts,
            local_name,
        )

    def _wildcard_elastic_index_name(self) -> str:
        return self._full_elastic_index_name("*")

    def build_index_action(self, doc_id, doc_source):
        return {
            "_op_type": "index",
            "_id": str(doc_id),
            "_source": doc_source,
        }

    def build_delete_action(self, doc_id):
        return {
            "_op_type": "delete",
            "_id": str(doc_id),
        }

    def build_update_action(self, doc_id, doc_source):
        return {
            "_op_type": "update",
            "_id": str(doc_id),
            "doc": doc_source,
        }

    def _ensure_elastic_index(self, local_name: str) -> None:
        _config = self._local_indexes()[local_name]
        assert _config['local_name'] == local_name
        logger.debug("Ensuring index %s", local_name)
        if not self.es8_client.indices.exists(index=local_name):
            logger.info("Creating index %s", local_name)
            (
                self.es8_client.indices.create(
                    index=local_name,
                    settings=_config["settings"],
                    mappings=_config["mappings"],
                )
            )
            self.pls_refresh()

    def _get_partindex_status(self, local_name: str) -> IndexStatus:
        if not self.pls_check_exists():
            return IndexStatus(
                index_subname=self.subindex_name,
                specific_indexname=self.full_index_name,
                is_kept_live=False,
                doc_count=0,
                creation_date="",
            )
        index_info = self.shtrove_index.es8_client.indices.get(
            index=self.full_index_name, features="aliases,settings"
        )[self.full_index_name]
        index_aliases = set(index_info["aliases"].keys())
        creation_date = timestamp_to_readable_datetime(
            index_info["settings"]["index"]["creation_date"]
        )
        doc_count = self.shtrove_index.es8_client.indices.stats(
            index=self.full_index_name, metric="docs"
        )["indices"][self.full_index_name]["primaries"]["docs"]["count"]
        return IndexStatus(
            index_subname=self.subindex_name,
            specific_indexname=self.full_index_name,
            is_kept_live=(self.shtrove_index._alias_for_keeping_live in index_aliases),
            creation_date=creation_date,
            doc_count=doc_count,
        )

    def each_existing_index(
        self, *, any_strategy_check: bool = False
    ) -> typing.Iterator[SpecificElastic8Index]:
        _index_wildcard = (
            combine_indexname_parts(self.strategy_name, "*")
            if any_strategy_check
            else self.indexname_wildcard
        )
        indexname_set = set(
            self.es8_client.indices.get(index=_index_wildcard, features=",").keys()
        )
        for indexname in indexname_set:
            _index = self.parse_full_index_name(indexname)
            assert _index.shtrove_index.strategy_name == self.strategy_name
            yield _index

    def each_live_index(self, *, any_strategy_check: bool = False):
        for _indexname in self._get_indexnames_for_alias(self._alias_for_keeping_live):
            _index = self.parse_full_index_name(_indexname)
            if any_strategy_check or (_index.shtrove_index == self):
                yield _index

    def do_teardown(self, *, really_really: bool) -> None:
        if really_really:
            for _index in self.each_existing_index():
                _index.pls_delete()

    def pls_check_exists(self) -> bool:
        return all(_index.pls_check_exists() for _index in self.each_subnamed_index())

    def pls_refresh(self, local_name: str | None = None) -> None:
        _to_refresh = (
            self._wildcard_elastic_index_name()
            if local_name is None
            else self._full_elastic_index_name(local_name)
        )
        self.es8_client.indices.refresh(index=_to_refresh)
        logger.info("%s: Refreshed", _to_refresh)

    def pls_start_keeping_live(self):
        for _index in self.each_subnamed_index():
            _index.pls_start_keeping_live()

    def pls_stop_keeping_live(self):
        for _index in self.each_live_index():
            _index.pls_stop_keeping_live()

    def _send_elastic_action(self):
        self.assert_message_type(messages_chunk.message_type)
        _action_tracker = _ActionTracker()
        _bulk_stream = streaming_bulk(
            self.es8_client,
            self._elastic_actions_with_index(messages_chunk, _action_tracker),
            raise_on_error=False,
            max_retries=settings.ELASTICSEARCH["MAX_RETRIES"],
        )
        _affected_indexnames: set[str] = set()
        for _ok, _response in _bulk_stream:
            _op_type, _response_body = next(iter(_response.items()))
            _status = _response_body.get("status")
            _docid = _response_body["_id"]
            _indexname = _response_body["_index"]
            _affected_indexnames.add(_indexname)
            _is_done = _ok or (_op_type == "delete" and _status == 404)
            if _is_done:
                _finished_message_id = _action_tracker.action_done(_indexname, _docid)
                if _finished_message_id is not None:
                    yield messages.IndexMessageResponse(
                        is_done=True,
                        index_message=messages.IndexMessage(
                            messages_chunk.message_type, _finished_message_id
                        ),
                        status_code=HTTPStatus.OK.value,
                        error_text=None,
                    )
                    _action_tracker.forget_message(_finished_message_id)
            else:
                _action_tracker.action_errored(_indexname, _docid)
                yield messages.IndexMessageResponse(
                    is_done=False,
                    index_message=messages.IndexMessage(
                        messages_chunk.message_type,
                        _action_tracker.get_message_id(_docid),
                    ),
                    status_code=_status,
                    error_text=str(_response_body),
                )
        for _message_id in _action_tracker.remaining_done_messages():
            yield messages.IndexMessageResponse(
                is_done=True,
                index_message=messages.IndexMessage(
                    messages_chunk.message_type, _message_id
                ),
                status_code=HTTPStatus.OK.value,
                error_text=None,
            )
        self.after_chunk(messages_chunk, _affected_indexnames)

    # abstract method from ShareIndexStrategy
    def pls_make_default_for_searching(self):
        self._set_indexnames_for_alias(
            self._alias_for_searching,
            {self.indexname_wildcard},
        )

    # abstract method from ShareIndexStrategy
    def pls_get_default_for_searching(self) -> ShareIndexStrategy | None:
        _searchnames = self._get_indexnames_for_alias(self._alias_for_searching)
        try:
            _indexname, *_ = _searchnames
        except ValueError:
            return None  # no default set
        _strategyname, _strategycheck, *_ = parse_indexname_parts(_indexname)
        assert _strategyname == self.strategy_name
        _strategycheck = _strategycheck.rstrip("*")  # may be a wildcard alias
        return self.with_strategy_check(_strategycheck)

    # override from ShareIndexStrategy
    def pls_refresh(self):
        super().pls_refresh()  # refreshes each index
        logger.debug("%s: Waiting for yellow status", self.strategy_name)
        self.es8_client.cluster.health(wait_for_status="yellow")

    @property
    def _alias_for_searching(self):
        return combine_indexname_parts(self.strategy_name, "search")

    @property
    def _alias_for_keeping_live(self):
        return combine_indexname_parts(self.strategy_name, "live")

    def _elastic_actions_with_index(
        self,
        messages_chunk: messages.MessagesChunk,
        action_tracker: _ActionTracker,
    ):
        for _actionset in self.build_elastic_actions(messages_chunk):
            for (
                _index_subname,
                _elastic_actions,
            ) in _actionset.actions_by_subname.items():
                _indexnames = self._get_indexnames_for_action(
                    index_subname=_index_subname,
                    is_backfill_action=messages_chunk.message_type.is_backfill,
                )
                for _elastic_action in _elastic_actions:
                    _docid = _elastic_action["_id"]
                    for _indexname in _indexnames:
                        action_tracker.add_action(
                            _actionset.message_target_id, _indexname, _docid
                        )
                        _elastic_action_with_index = {
                            **_elastic_action,
                            "_index": _indexname,
                        }
                        logger.debug(
                            "%s: elastic action: %r", self, _elastic_action_with_index
                        )
                        yield _elastic_action_with_index
            action_tracker.done_scheduling(_actionset.message_target_id)

    def _get_indexnames_for_action(
        self,
        index_subname: str,
        *,
        is_backfill_action: bool = False,
    ) -> set[str]:
        if is_backfill_action:
            return {self.get_index(index_subname).full_index_name}
        return {
            _index.full_index_name
            for _index in self.each_live_index()
            if _index.subindex_name == index_subname
        }

    def _get_indexnames_for_alias(self, alias_name) -> set[str]:
        try:
            aliases = self.es8_client.indices.get_alias(name=alias_name)
            return set(aliases.keys())
        except elasticsearch8.exceptions.NotFoundError:
            return set()

    def _add_indexname_to_alias(self, alias_name, indexname):
        self.es8_client.indices.update_aliases(
            actions=[
                {"add": {"index": indexname, "alias": alias_name}},
            ]
        )

    def _remove_indexname_from_alias(self, alias_name, indexname):
        self.es8_client.indices.update_aliases(
            actions=[
                {"remove": {"index": indexname, "alias": alias_name}},
            ]
        )

    def _set_indexnames_for_alias(self, alias_name, indexnames):
        already_aliased = self._get_indexnames_for_alias(alias_name)
        want_aliased = set(indexnames)
        if already_aliased == want_aliased:
            logger.info(
                f'alias "{alias_name}" already correct ({want_aliased}), doing nothing'
            )
        else:
            to_remove = tuple(already_aliased - want_aliased)
            to_add = tuple(want_aliased - already_aliased)
            logger.warning(
                f'alias "{alias_name}": removing indexes {to_remove} and adding indexes {to_add}'
            )
            self.es8_client.indices.update_aliases(
                actions=[
                    *(
                        {"remove": {"index": indexname, "alias": alias_name}}
                        for indexname in to_remove
                    ),
                    *(
                        {"add": {"index": indexname, "alias": alias_name}}
                        for indexname in to_add
                    ),
                ]
            )


@dataclasses.dataclass
class SpecificElastic8Index:
    es8_client: elasticsearch8.Elasticsearch
    shtrove_index: ShareLegacyElastic8Strategy
    subindex_name: str  # unique per shtrove_index

    def pls_check_exists(self):
        _indexname = self.full_index_name
        _result = bool(self.shtrove_index.es8_client.indices.exists(index=_indexname))
        logger.info(
            f"{_indexname}: exists" if _result else f"{_indexname}: does not exist"
        )
        return _result

    def pls_delete(self):
        _indexname = self.full_index_name
        (
            self.shtrove_index.es8_client.indices.delete(
                index=_indexname, ignore=[400, 404]
            )
        )
        logger.warning("%s: deleted", _indexname)

    def pls_start_keeping_live(self):
        self.shtrove_index._add_indexname_to_alias(
            indexname=self.full_index_name,
            alias_name=self.shtrove_index._alias_for_keeping_live,
        )
        logger.info("%r: now kept live", self)

    def pls_stop_keeping_live(self):
        self.shtrove_index._remove_indexname_from_alias(
            indexname=self.full_index_name,
            alias_name=self.shtrove_index._alias_for_keeping_live,
        )
        logger.warning("%r: no longer kept live", self)

    def pls_get_mappings(self):
        return self.shtrove_index.es8_client.indices.get_mapping(
            index=self.full_index_name
        ).body
