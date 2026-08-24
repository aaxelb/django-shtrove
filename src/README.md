# source code for shtrove and django_shtrove

- `src/shtrove/`: interfaces and basic tools for troving and sharing catalog records
    - interface types (python protocols) for different clusters of metadata-catalog functionality:
        - `ProtoExtract`: parse metadata from a document
        - `ProtoPersist`: store (and browse) metadata as catalog records
        - `ProtoIndex`: index (and search) metadata from catalog records
        - `ProtoDerive`: serialize a catalog record following some metadata format
        - `ProtoRender`: serialize a shtrove api response following some api standard
        - `ProtoShtrove`: tie the rest together for easy ingest, browse, and search
    - basic (no-django) implementations of some of those interfaces:
        - `ProtoExtract` implementations: `TurtleExtract`
        - `ProtoRender` implementations: `HtmlRender`, `JsonApiRender`, `JsonLdRender`, `TurtleRender`
        - shtrove: `BasicShtrove`
            - requires a given `ProtoPersist`
            - for search, requires one or more given `ProtoIndex`
            - for derived metadata formats, can give one or more `ProtoDerive`
            - supports all extract/render implementations
    - does NOT use or depend on anything from `django` or `django_shtrove`

- `src/django_shtrove/`: installable django app that provides:
    - `DjangoShtrovePersist`: a `ProtoPersist` implementation using django models 
    - `ShtrovesearchElastic8`: a `ProtoIndex` implementation using elasticsearch8
    - `DjangoShtrove`: a `ProtoShtrove` implementation configured from django project settings
    - django views and urls for searching and browsing a given `ProtoShtrove`
        - `/browse`
        - `/record-search`
        - `/value-search`
        - using [http content negotiation](https://www.rfc-editor.org/info/rfc9110/#content.negotiation)
          to select a `ProtoRender` for each response

