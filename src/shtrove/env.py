"""environment variables used to configure SHTROVE"""

import os


def parse_list(env_value: str, *, delimiter: str = ",") -> list[str]:
    """
    >>> parse_list('hello,goodbye')
    ['hello', 'goodbye']
    >>> parse_list(' goodbye , , hello ')
    ['goodbye', 'hello']
    >>> parse_list('')
    []
    """
    _each_segment = (_segment.strip() for _segment in env_value.split(delimiter))
    return list(filter(None, _each_segment))


# one or more available extract strategies
SHTROVE_EXTRACT_STRAT_PY = parse_list(
    os.environ.get(
        "SHTROVE_EXTRACT_STRAT_PY_LIST",
        "shtrove.derive.basic.TurtleExtract",
    ),
)
# exactly one persist strategy, since it mints record uuids and acts as source of truth
# (if you want to persist multiple ways, implement a single ProtoPersist
# that coordinates among them however you want to provide a consistent interface)
SHTROVE_PERSIST_STRAT_PY = os.environ.get(
    "SHTROVE_PERSIST_STRAT_PY",
    "shtrove.persist.basic.BasicFiletreePersist",  # TODO
)
# zero or more parallel derive strategies
SHTROVE_DERIVE_STRAT_PY_LIST = parse_list(
    os.environ.get("SHTROVE_DERIVE_STRAT_PY_LIST") or ""
)
# zero or more parallel index strategies
SHTROVE_INDEX_STRAT_PY_LIST = parse_list(
    os.environ.get("SHTROVE_INDEX_STRAT_PY_LIST") or ""
)
# one or more available render strategies
SHTROVE_RENDER_STRAT_PY_LIST = parse_list(
    os.environ.get(
        "SHTROVE_RENDER_STRAT_PY_LIST",
        "shtrove.derive.basic.TurtleExtract",
    ),
)
