"""utilities for working with django querysets"""

from __future__ import annotations
import collections.abc as _abc
import typing

if typing.TYPE_CHECKING:
    from django.db.models import Model
    from django.db.models.query import QuerySet

    _M = typing.TypeVar("_M", bound=Model)


__all__ = ("pk_chunked",)


def pk_chunked(queryset: QuerySet[_M], chunksize: int) -> _abc.Generator[list[_M]]:
    """pk_chunked: get primary key values, in chunks, for the given queryset

    yields non-empty lists of primary keys up to `chunksize` long
    """
    _ordered_qs = queryset.order_by("pk")
    _prior_end_pk = None
    _chunk_qs: QuerySet[_M] | None = _ordered_qs
    while _chunk_qs is not None:  # for each chunk:
        # load primary key values only
        _pks = list(_chunk_qs.values_list("pk", flat=True)[:chunksize])
        if _pks:
            _end_pk = _pks[-1]
            if (_prior_end_pk is not None) and (_end_pk <= _prior_end_pk):
                raise RuntimeError(
                    f"sentinel pks not ascending?? got {_end_pk} after {_prior_end_pk}"
                )
            yield _pks
            _prior_end_pk = _end_pk
            _chunk_qs = _ordered_qs.filter(pk__gt=_prior_end_pk)
        else:
            _chunk_qs = None  # done
