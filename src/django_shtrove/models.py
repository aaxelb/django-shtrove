"""
TODO:

models from SHARE/trove:
- ResourceIdentifier
- Indexcard
- DerivedIndexcard
- ResourceDescription (abstract)
    - LatestResourceDescription
    - ArchivedResourceDescription
    - SupplementaryResourceDescription
- IndexBackfill

note: replace `Indexcard.source_record_suid`, `SupplementaryResourceDescription.supplementary_suid`
with an identifier field (or configurable fk field?) with unique constraint
"""
from django.db import models

# Create your models here.
