# django-shtrove

a django app (and assorted tools) to share a trove of (meta)data

> share (verb): to have or use in common.

> trove (noun): a store of valuable or delightful things.

(a work in progress -- see [_TODO.md](./_TODO.md) for plans and details)

## contents

### shtrove
a python package with abstract interfaces and basic tools for troving and sharing (meta)data

- defines types (python protocols) for clusters of metadata-catalog functionality:
    - `ProtoExtract`: parse metadata from a document
    - `ProtoPersist`: store (and browse) metadata as catalog records
    - `ProtoIndex`: index (and search) metadata from catalog records
    - `ProtoDerive`: serialize a catalog record following some metadata format
    - `ProtoRender`: serialize a shtrove api response following some api standard
    - `ProtoShtrove`: tie the rest together with methods for ingest, browse, and search
- has basic imp(lamentation)s of some of those interfaces:
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

### django_shtrove
a django app that provides:
- `DjangoShtrove`: a `ProtoShtrove` implementation configured from django project settings
- `DjangoShtrovePersist`: a `ProtoPersist` implementation using django models 
- `ShtrovesearchElastic8`: a `ProtoIndex` implementation using elasticsearch8
- django views for searching and browsing a given `ProtoShtrove`
    - default url namespace:
        - `/browse`: look up records by given identifier
        - `/record-search`: find records matching given search filters and text
        - `/value-search`: find values used at given metadata property paths
        - `/oai-pmh`: 
    - selects a `ProtoRender` for each response using
      [http content negotiation](https://www.rfc-editor.org/info/rfc9110/#content.negotiation)

## installation
(TODO: pypi -- for now, install from a local dir or from github...)

## use in a django project
in your project settings:
- add `"django_shtrove"` to `INSTALLED_APPS`
- configure... (TODO)
