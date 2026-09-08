import abc
from collections.abc import Mapping
import dataclasses
import functools
from http import HTTPStatus
import logging
import types
import typing

from django.conf import settings
import elasticsearch8
from elasticsearch8.helpers import streaming_bulk

from django_shtrove.shtrove_imps.index._base import ShareIndexStrategy
from shtrove import types as _types
from shtrove.imps.index import (
    ShtroveIndexStatus,
    ShtroveSubindexStatus,
)
from shtrove.imps.checksum import Checksum
from shtrove.util.json import JsonObject
from share.search.index_status import IndexStatus
from share.search import messages
from share.search.index_strategy._util import timestamp_to_readable_datetime
from ._indexnames import (
    parse_indexname_parts,
    combine_indexname_parts,
)

logger = logging.getLogger(__name__)


class ElasticIndexDefinition(typing.TypedDict):
    mappings: JsonObject
    settings: JsonObject


class ShareLegacyElastic8Strategy(_types.ProtoIndex, abc.ABC):
    """abstract base class for index strategies using elasticsearch 8"""

    ###
    # abstract methods for subclasses to implement

    @classmethod
    @abc.abstractmethod
    def define_current_indexes(cls) -> dict[str, ElasticIndexDefinition]:
        raise NotImplementedError

    @abc.abstractmethod
    def set_metadatum(self, metadata: _types.ProtoCombinedMetadata) -> None: ...

    ###
    # helper methods for subclasses to use (or override)

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

    ###
    # implementation for subclasses to ignore

    # for IndexSetup
    def do_initial_setup(self) -> None:
        for _index_def in self.current_elastic_index_defs():
            self._create_elastic_index(
            

    # for IndexSetup
    def do_update_setup(self) -> None:
        self.pls_setup()  # TODO?

    @abc.abstractmethod
    def do_teardown(self, *, really_really: bool) -> None:
        raise NotImplementedError

    def get_index_status(self) -> _indextypes.ProtoIndexStatus:
        _subindex_statuses: list[_indextypes.ProtoSubindexStatus] = []
        _prior_strategy_statuses: list[_indextypes.ProtoIndexStatus] = []
        if self.is_current:
            _subindex_statuses = [
                _index.pls_get_status() for _index in self.each_subnamed_index()
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
            _subindex_statuses = [
                _index.pls_get_status() for _index in self.each_existing_index()
            ]
        return ShtroveIndexStatus(
            strategy_name=self.strategy_name,
            strategy_check=self.strategy_check,
            is_set_up=self.pls_check_exists(),
            is_default_for_searching=(self == self.pls_get_default_for_searching()),
            index_statuses=_subindex_statuses,
            existing_prior_strategies=_prior_strategy_statuses,
        )


    # abstract method from ShareIndexStrategy
    @classmethod
    def compute_current_config_checksum(cls):
        _current_defs = cls.current_index_defs()
        if "" in _current_defs and len(_current_defs) == 1:
            _current_defs = _current_defs[""]
        return ChecksumIri.digest_json(
            checksumalgorithm_name="sha-256",
            salt=cls.__name__,
            raw_json=_current_json,  # type: ignore[arg-type]
        )

    # abstract method from ShareIndexStrategy
    @classmethod
    def each_index_subname(self) -> typing.Iterable[str]:
        yield from self.current_index_defs().keys()

    @classmethod
    @functools.cache
    def current_index_defs(cls) -> Mapping[str, ElasticIndexDefinition]:
        # readonly and cached per class
        return types.MappingProxyType(cls.define_current_indexes())

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

    def pls_refresh(self) -> None:
        for _index in self.each_subnamed_index():
            _index.pls_refresh()

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

    @property
    def is_current(self) -> bool:
        return self.shtrove_index.is_current

    @property
    def has_valid_subname(self) -> bool:
        return self.subindex_name in self.shtrove_index.index_subname_set()

    @property
    def full_index_name(self) -> str:
        return indexnames.combine_indexname_parts(
            *self.shtrove_index.indexname_prefix_parts,
            self.subindex_name,
        )

    @property
    def index_def(self) -> ElasticIndexDefinition:
        return self.shtrove_index.current_index_defs()[self.subindex_name]

    def pls_get_status(self) -> IndexStatus:
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

    def pls_check_exists(self):
        _indexname = self.full_index_name
        _result = bool(self.shtrove_index.es8_client.indices.exists(index=_indexname))
        logger.info(
            f"{_indexname}: exists" if _result else f"{_indexname}: does not exist"
        )
        return _result

    def pls_create(self):
        assert self.is_current, "cannot create a non-current version of an index!"
        index_to_create = self.full_index_name
        logger.debug("Ensuring index %s", index_to_create)
        index_exists = self.shtrove_index.es8_client.indices.exists(
            index=index_to_create
        )
        if not index_exists:
            logger.info("Creating index %s", index_to_create)
            _index_def = self.index_def
            (
                self.shtrove_index.es8_client.indices.create(
                    index=index_to_create,
                    settings=_index_def.settings,
                    mappings=_index_def.mappings,
                )
            )
            self.pls_refresh()

    def pls_refresh(self):
        _indexname = self.full_index_name
        (self.shtrove_index.es8_client.indices.refresh(index=_indexname))
        logger.info("%s: Refreshed", _indexname)

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
