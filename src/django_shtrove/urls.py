"""
TODO:
- urls (align with readme, improve from trove):
    - `/browse`: look up records by given identifier
    - `/record-search`: find records matching given search filters and text
    - `/value-search`: find values used at given metadata property paths
    - `/oai-pmh`?
    - `/docs`?
    - `/vocab`?
    - rss/atom feeds?
--

from trove.urls (to be included under a "/shtrove" prefix, for example)
- /index-card/<uuid:indexcard_uuid>
- /index-card-search
- /index-value-search
- /index-card-search/rss.xml
- /index-card-search/atom.xml
- /browse
- /docs/openapi.json
- /docs/openapi.html
- /docs

from SHARE's project.urls:
- /oai-pmh

new django-shtrove urls (e.g.)
- /shtrove/vocab/2023/<path:vocab_term> -- vocab namespace for defined shtrove terms

(optional) add to osf urls:
- osf.example/vocab/2022/<path:vocab_term> -- vocab namespace for existing defined OSFMAP terms
"""
