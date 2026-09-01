# django_shtrove
a python package with tools for troving and sharing (meta)data using
[shtrove](../shtrove/README.md) and django

- `DjangoShtrovePersist`: a `shtrove.ProtoPersist` implementation using django models 
- `ShtrovesearchElastic8`: a `shtrove.ProtoIndex` implementation using elasticsearch8
- `DjangoShtrove`: a `shtrove.ProtoShtrove` implementation configured from django project settings
- django views for searching and browsing a given `shtrove.ProtoShtrove`
    - `django_shtrove.urls` url namespace contains:
        - `/browse`: look up records by given identifier
        - `/record-search`: find records matching given search filters and text
        - `/value-search`: find values used at given metadata property paths
        - `/oai-pmh`?
        - `/docs`?
    - selects a `ProtoRender` for each response using
      [http content negotiation](https://www.rfc-editor.org/info/rfc9110/#content.negotiation)
