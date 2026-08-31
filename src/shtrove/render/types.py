"""shtrove.render.types: interface for rendering shtrove api responses"""

__all__ = (
    "ProtoRender",
    "ProtoRendering",
    "RenderingFlags",
)

import collections.abc as _abc
import enum
import typing

from primitive_metadata import gather


class RenderingFlags(enum.Flag):
    INCREMENTAL = enum.auto()


class ProtoRendering(typing.Protocol):
    mediatype: str
    rendering_flags: RenderingFlags = RenderingFlags(0)

    def each_content_segment(self) -> _abc.Iterator[str] | _abc.Iterator[bytes]: ...


@typing.runtime_checkable
class ProtoRender(typing.Protocol):
    @classmethod
    def mediatype(self) -> str: ...

    def render_response(
        self, focus: gather.Focus, gathering: gather.Gathering
    ) -> ProtoRendering: ...
