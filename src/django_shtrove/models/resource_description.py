from __future__ import annotations
import datetime

from django.db import models
from primitive_metadata import primitive_rdf as rdf

__all__ = (
    "ArchivedResourceDescription",
    "ResourceDescription",
    "LatestResourceDescription",
    "SupplementaryResourceDescription",
)


class ResourceDescription(models.Model):
    """
    abstract base class for models storing an rdf graph that belongs to an indexcard
    """

    # auto:
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    # required:
    indexcard = models.ForeignKey(
        "trove.Indexcard",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_set",
    )
    turtle_checksum_iri = models.TextField(db_index=True)
    focus_iri = models.TextField()  # exact iri used in rdf_as_turtle
    rdf_as_turtle = models.TextField()  # TODO: store elsewhere by checksum

    # optional:
    expiration_date = models.DateField(
        null=True,
        blank=True,
        help_text="An (optional) date when this description will no longer be valid.",
    )

    class Meta:
        abstract = True

    @property
    def is_expired(self) -> bool:
        return (
            self.expiration_date is not None
            and self.expiration_date <= datetime.date.today()
        )

    def as_rdf_tripledict(self) -> rdf.RdfTripleDictionary:
        return rdf.tripledict_from_turtle(self.rdf_as_turtle)

    def as_quoted_graph(self) -> rdf.QuotedGraph:
        return rdf.QuotedGraph(
            self.as_rdf_tripledict(),
            focus_iri=self.focus_iri,
        )

    def as_rdfdoc_with_supplements(self) -> rdf.RdfGraph:
        """build an rdf graph composed of this rdf and all current card supplements"""
        _rdfdoc = rdf.RdfGraph(self.as_rdf_tripledict())
        for _supplement in self.indexcard.supplementary_description_set.all():
            _rdfdoc.add_tripledict(_supplement.as_rdf_tripledict())
        return _rdfdoc

    def __repr__(self) -> str:
        return f'<{self.__class__.__qualname__}({self.pk}, "{self.focus_iri}")'

    def __str__(self) -> str:
        return repr(self)


class LatestResourceDescription(ResourceDescription):
    """
    core descriptive metadata about this indexcard's focus resource -- only the most recent
    """

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("indexcard",),
                name="%(app_label)s_%(class)s_uniq_indexcard",
            ),
        ]
        indexes = [
            models.Index(fields=("modified",)),  # for OAI-PMH selective harvest
            models.Index(fields=["expiration_date"]),  # for expiring
        ]


class ArchivedResourceDescription(ResourceDescription):
    """
    core descriptive metadata about this indexcard's focus resource -- all versions over time
    """

    pass


class SupplementaryResourceDescription(ResourceDescription):
    """
    supplementary (non-descriptive or "administrative") metadata -- only the most recent
    """

    supplementary_record_identifier = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("indexcard", "supplementary_record_identifier"),
                name="%(app_label)s_%(class)s_uniq_indexcard_supplement",
            ),
        ]
        indexes = [
            models.Index(fields=["expiration_date"]),  # for expiring
        ]
