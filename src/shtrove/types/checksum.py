import typing

__all__ = ("ProtoChecksum",)


class ProtoChecksum(typing.Protocol):
    @property
    def hash_name(self) -> str: ...
    @property
    def prefix(self) -> str: ...
    @property
    def hexdigest(self) -> str: ...
