"""shtrove.render.proto: interface for rendering shtrove api responses
"""
import enum
import typing

from shtrove.proto import (
    ProtoCatalogRecord,
    ProtoCombinedMetadata,
)


class ProtoRenderStrategy(typing.Protocol):
    def render_response(self, focus: gather.Focus, gathering: gather.Gathering) -> ProtoRendering: ...


class RenderingFlags(enum.Flags):
    INCREMENTAL = enum.auto()


class ProtoRendering(typing.Protocol):
    mediatype: str
    rendering_flags: RenderingFlags = RenderingFlags(0)

    def each_content_segment(self) -> Iterator[str] | Iterator[bytes]: ...
