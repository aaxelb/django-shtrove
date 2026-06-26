"""
TODO:

admin classes from SHARE/trove:
- trove.admin.ResourceIdentifierAdmin
- trove.admin.IndexcardAdmin
- trove.admin.LatestResourceDescriptionAdmin
- trove.admin.ArchivedResourceDescriptionAdmin
- trove.admin.SupplementaryResourceDescriptionAdmin
- trove.admin.DerivedIndexcardAdmin
- share.admin.IndexBackfillAdmin

with helpful utilities used thereby:
- share.admin.util.TimeLimitedPaginator
- share.admin.util.linked_fk
- share.admin.util.linked_many

and search-indexes admin view:
- share.admin.search
- urls from share.admin.ShareAdminSite.get_urls
- templates:
    - share/templates/admin/search-indexes.html
    - linked from nav-global block in share/templates/admin/base_site.html
"""
from django.contrib import admin

# Register your models here.
