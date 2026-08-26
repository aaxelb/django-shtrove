__all__ = (
    'load_entry_point',
    'load_each_entry_point',
)
from importlib.metadata import entry_points


def load_entry_point(group: str, name: str):
    (_ep,) = entry_points(group=group, name=name)
    return _ep.load()


def load_each_entry_point(group: str):
    for _ep in entry_points(group=group):
        yield _ep.load()
