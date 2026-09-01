from __future__ import annotations
from collections.abc import Callable
import dataclasses
import hashlib
import json
from typing import Self, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from shtrove.util.json import JsonValue


type HexdigestFn = Callable[[str | bytes, str | bytes], str]


def _ensure_bytes(bytes_or_something: bytes | str) -> bytes:
    if isinstance(bytes_or_something, bytes):
        return bytes_or_something
    if isinstance(bytes_or_something, str):
        return bytes_or_something.encode()
    raise NotImplementedError(f"how bytes? ({bytes_or_something})")


def _builtin_checksum(hash_constructor: Any) -> HexdigestFn:
    def hexdigest_fn(prefix: str | bytes, data: str | bytes) -> str:
        hasher = hash_constructor()
        hasher.update(_ensure_bytes(prefix))
        hasher.update(_ensure_bytes(data))
        return str(hasher.hexdigest())

    return hexdigest_fn


CHECKSUM_ALGORITHMS = {
    "sha-256": _builtin_checksum(hashlib.sha256),
    "sha-384": _builtin_checksum(hashlib.sha384),
    "sha-512": _builtin_checksum(hashlib.sha512),
}

DEFAULT_CHECKSUM_ALGORITHM_NAME = "sha-256"


@dataclasses.dataclass(frozen=True)
class Checksum:
    hash_name: str
    prefix: str
    hexdigest: str

    def as_iri(self) -> str:
        return (
            f"urn:checksum:{self.hash_name}:{self.prefix}:{self.hexdigest}"
        )

    @classmethod
    def digest(
        cls,
        *,
        algorithm: str = DEFAULT_CHECKSUM_ALGORITHM_NAME,
        prefix: str = "",
        data: str,
    ) -> Self:
        try:
            hexdigest_fn = CHECKSUM_ALGORITHMS[algorithm]
        except KeyError:
            raise ValueError(
                f'unknown checksum algorithm "{algorithm}"'
                f" (would recognize {set(CHECKSUM_ALGORITHMS.keys())})"
            )
        return cls(
            hash_name=algorithm,
            prefix=prefix,
            hexdigest=hexdigest_fn(prefix, data),
        )

    @classmethod
    def digest_json(
        cls,
        *,
        algorithm: str = DEFAULT_CHECKSUM_ALGORITHM_NAME,
        prefix: str = "",
        raw_json: JsonValue,
    ) -> Self:
        return cls.digest(
            algorithm=algorithm,
            prefix=prefix,
            data=json.dumps(raw_json, sort_keys=True),
        )

    @classmethod
    def from_iri(cls, checksum_iri: str) -> Self:
        # TODO: more iris? now "urn:checksum:..."; could do "magnet:..." or "checksum:" or something spdx?
        try:
            urn, checksum, algorithmname, prefix, hexdigest = checksum_iri.split(":")
            assert (urn, checksum) == ("urn", "checksum")
            # TODO: checks on algorithmname, prefix, hexdigest
        except (ValueError, AssertionError):
            raise ValueError(f'invalid checksum iri "{checksum_iri}"')
        return cls(
            hash_name=algorithmname,
            prefix=prefix,
            hexdigest=hexdigest,
        )
