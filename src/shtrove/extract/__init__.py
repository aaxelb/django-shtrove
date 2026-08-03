"""shtrove.extract
"""

class ProtoIndexStrategy(typing.Protocol):
    def add(self, record: ProtoShtroveRecord) -> 


class IndexStrategy(type[ProtoIndexStrategy]):
    @classmethod
