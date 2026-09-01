# shtrove
a python package with abstract interfaces and basic tools for troving and sharing (meta)data

- in `shtrove.types`, defines types (python protocols) for clusters of metadata-catalog functionality:
    - `ProtoExtract`: parse rdf (meta)data from a digital document
    - `ProtoPersist`: store and browse (meta)data as catalog records
    - `ProtoIndex`: index and search (meta)data from catalog records
    - `ProtoDerive`: serialize a catalog record following some (meta)data format
    - `ProtoRender`: serialize a shtrove api response following some api standard
    - `ProtoShtrove`: tie the rest together with methods for ingest, browse, and search
- in `shtrove.imps`, basic imp(lamentation)s of some of those interfaces:
    - `ProtoExtract`: `TurtleExtract`
    - `ProtoRender`:`HtmlRender`, `JsonApiRender`, `JsonLdRender`, `TurtleRender`
    - `ProtoShtrove`: `BasicShtrove`
        - requires a given `ProtoPersist`
        - for search, requires one or more given `ProtoIndex`
        - for derived metadata formats, can give one or more `ProtoDerive`
        - uses any available `ProtoExtract` and `ProtoRender`, selected by mediatype
- [uses python entry points](https://packaging.python.org/en/latest/specifications/entry-points/)
  to find available implementations
    - an entry-point group for each shtrove protocol:
        - `shtrove.ProtoExtract`
        - `shtrove.ProtoPersist`
        - `shtrove.ProtoIndex`
        - `shtrove.ProtoDerive`
        - `shtrove.ProtoRender`
        - `shtrove.ProtoShtrove`
- does NOT use or depend on anything from `django` or `django_shtrove`
