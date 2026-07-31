from __future__ import annotations
import datetime
import uuid
from typing import Any

from django.db import models
from django.db import transaction
from django.utils import timezone
from primitive_metadata import primitive_rdf as rdf

from django_shtrove.models.derived_indexcard import DerivedIndexcard
from django_shtrove.models.resource_description import (
    ArchivedResourceDescription,
    ResourceDescription,
    LatestResourceDescription,
    SupplementaryResourceDescription,
)
from django_shtrove.models.resource_identifier import ResourceIdentifier
from shtrove.util.checksum import Checksum
from shtrove.exceptions import DigestiveError
from shtrove.vocab.namespaces import RDF
from shtrove.vocab.trove import trove_indexcard_iri


__all__ = ('Indexcard',)


class IndexcardManager(models.Manager['Indexcard']):
    @transaction.atomic
    def save_indexcard_from_tripledict(
        self, *,
        rdf_tripledict: rdf.RdfTripleDictionary,
        focus_iri: str,
        restore_deleted: bool = False,
        expiration_date: datetime.date | None = None,
    ) -> Indexcard:
        _focus_identifier_set = (
            ResourceIdentifier.objects
            .save_equivalent_identifier_set(rdf_tripledict, focus_iri)
        )
        _focustype_identifier_set = [  # TODO: require non-zero?
            ResourceIdentifier.objects.get_or_create_for_iri(_iri)
            for _iri in rdf_tripledict[focus_iri].get(RDF.type, ())
        ]
        assert _focus_identifier_set
        _indexcard: Indexcard | None = Indexcard.objects.filter(
            focus_identifier_set__in=_focus_identifier_set,
        ).first()
        if _indexcard is None:
            _indexcard = Indexcard.objects.create()
        if restore_deleted and _indexcard.deleted:
            _indexcard.deleted = None
            _indexcard.save()
        _indexcard.focus_identifier_set.set(_focus_identifier_set)
        _indexcard.focustype_identifier_set.set(_focustype_identifier_set)
        _indexcard.update_resource_description(focus_iri, rdf_tripledict, expiration_date=expiration_date)
        return _indexcard

    @transaction.atomic
    def supplement_indexcards(
        self, *,
        supplementary_record_identifier: str,
        rdf_tripledict: rdf.RdfTripleDictionary,
        focus_iri: str,
        expiration_date: datetime.date | None = None,
    ) -> list[Indexcard]:
        # supplement indexcards with the same focus
        # (if none exist, fine, nothing gets supplemented)
        _indexcards = list(Indexcard.objects.filter(
            focus_identifier_set__in=ResourceIdentifier.objects.queryset_for_iri(focus_iri),
        ))
        for _indexcard in _indexcards:
            _indexcard.update_supplementary_description(
                supplementary_record_identifier=supplementary_record_identifier,
                rdf_tripledict=rdf_tripledict,
                focus_iri=focus_iri,
                expiration_date=expiration_date,
            )
        return _indexcards


class Indexcard(models.Model):
    objects = IndexcardManager()

    # auto:
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)  # for public-api id
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    # optional:
    deleted = models.DateTimeField(null=True, blank=True)

    # relations:
    focus_identifier_set = models.ManyToManyField(
        ResourceIdentifier,
        related_name='indexcard_set',
    )
    focustype_identifier_set = models.ManyToManyField(
        ResourceIdentifier,
        related_name='+',
    )

    class Meta:
        indexes = [
            models.Index(fields=('deleted',)),
        ]

    @property
    def latest_resource_description(self) -> LatestResourceDescription:
        '''convenience for the "other side" of LatestResourceDescription.indexcard
        '''
        return self.trove_latestresourcedescription_set.get()  # may raise DoesNotExist

    @property
    def archived_description_set(self) -> Any:
        '''convenience for the "other side" of ArchivedResourceDescription.indexcard

        returns a RelatedManager
        '''
        return self.trove_archivedresourcedescription_set

    @property
    def supplementary_description_set(self) -> Any:
        '''convenience for the "other side" of SupplementaryResourceDescription.indexcard

        returns a RelatedManager
        '''
        return self.trove_supplementaryresourcedescription_set

    def get_semantic_iri(self) -> str:
        return trove_indexcard_iri(self.uuid)

    def pls_delete(self, *, notify_indexes: bool = True) -> None:
        # do not actually delete Indexcard, just mark deleted:
        if self.deleted is None:
            self.deleted = timezone.now()
            self.save()
        (  # actually delete LatestResourceDescription:
            LatestResourceDescription.objects
            .filter(indexcard=self)
            .delete()
        )
        (  # actually delete DerivedIndexcard:
            DerivedIndexcard.objects
            .filter(upriver_indexcard=self)
            .delete()
        )
        if notify_indexes:
            # TODO: rearrange to avoid local import
            from share.search.index_messenger import IndexMessenger
            IndexMessenger().notify_indexcard_update([self])

    def __repr__(self) -> str:
        return f'<{self.__class__.__qualname__}({self.uuid}, {self.source_record_suid})'

    def __str__(self) -> str:
        return repr(self)

    @transaction.atomic
    def update_resource_description(
        self,
        focus_iri: str,
        rdf_tripledict: rdf.RdfTripleDictionary,
        expiration_date: datetime.date | None = None,
    ) -> ResourceDescription:
        if focus_iri not in rdf_tripledict:
            raise DigestiveError(f'expected {focus_iri} in {set(rdf_tripledict.keys())}')
        _rdf_as_turtle, _turtle_checksum_iri = _turtlify(rdf_tripledict)
        _archived, _archived_created = ArchivedResourceDescription.objects.get_or_create(
            indexcard=self,
            turtle_checksum_iri=_turtle_checksum_iri,
            defaults={
                'rdf_as_turtle': _rdf_as_turtle,
                'focus_iri': focus_iri,
                'expiration_date': expiration_date,
            },
        )
        if (not _archived_created) and (_archived.rdf_as_turtle != _rdf_as_turtle):
            raise DigestiveError(f'hash collision? {_archived}\n===\n{_rdf_as_turtle}')
        if not self.deleted:
            _latest_resource_description, _created = LatestResourceDescription.objects.update_or_create(
                indexcard=self,
                defaults={
                    'turtle_checksum_iri': _turtle_checksum_iri,
                    'rdf_as_turtle': _rdf_as_turtle,
                    'focus_iri': focus_iri,
                    'expiration_date': expiration_date,
                },
            )
            return _latest_resource_description
        return _archived

    def update_supplementary_description(
        self,
        supplementary_record_identifier: str,
        focus_iri: str,
        rdf_tripledict: rdf.RdfTripleDictionary,
        expiration_date: datetime.date | None = None,
    ) -> SupplementaryResourceDescription:
        if focus_iri not in rdf_tripledict:
            raise DigestiveError(f'expected {focus_iri} in {set(rdf_tripledict.keys())}')
        _rdf_as_turtle, _turtle_checksum_iri = _turtlify(rdf_tripledict)
        _supplementary_rd, _ = SupplementaryResourceDescription.objects.update_or_create(
            indexcard=self,
            supplementary_record_identifier=supplementary_record_identifier,
            defaults={
                'turtle_checksum_iri': _turtle_checksum_iri,
                'rdf_as_turtle': _rdf_as_turtle,
                'focus_iri': focus_iri,
                'expiration_date': expiration_date,
            },
        )
        return _supplementary_rd


###
# local helpers

def _turtlify(rdf_tripledict: rdf.RdfTripleDictionary) -> tuple[str, str]:
    '''return turtle serialization and checksum iri of that serialization'''
    _rdf_as_turtle = rdf.turtle_from_tripledict(rdf_tripledict)
    _turtle_checksum_iri = Checksum.digest(data=_rdf_as_turtle).as_iri()
    return (_rdf_as_turtle, _turtle_checksum_iri)
