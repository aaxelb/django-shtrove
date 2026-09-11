# how this could relate to osf.io


## current state (with SHARE/trove as separate service)
(see [share doc](https://github.com/CenterForOpenScience/SHARE/blob/53de80c1a4831009db052b0517b90584e548f1d3/how-to/relate-to-osf.md#osf-thru-shtrove-ingestion-sequence))

```mermaid
sequenceDiagram
    box OSF
    participant oq as queues (rabbitmq)
    participant od as db (postgres)
    participant ow as worker (celery)
    end
    box shtrove
    participant ss as web server
    participant sd as db (postgres)
    participant sw as worker (celery)
    participant sq as queues (rabbitmq)
    participant si as indexer
    participant se as elasticsearch
    end
    oq -->> ow: receive update task
    od <<-->> ow: gather metadata
    ow ->> ss: POST /trove/ingest
    ss ->> sd: save metadata cards
    ss ->> sq: enqueue derive task
    ss ->> ow: 201 CREATED (success!)
    sq -->> sw: receive derive task
    sd <<-->> sw: load ResourceDescription(s)
    sw ->> sd: save DerivedIndexcards
    sw ->> sq: enqueue indexer message
    sq -->> si: bulk receive messages
    sd <<-->> si: bulk load metadata records
    si ->> se: bulk index
```

## hypotheticals of django-shtrove in osf.io
if using django-shtrove in osf.io, need to decide whether to keep the bulk indexer daemon from SHARE/trove

benefits of bulk indexing (hypothetical a):
- less contention with other background tasks over workers/queues
- faster/cheaper indexing of many records in a row, with fewer database queries

benefits of no bulk indexing (hypothetical b):
- one less daemon process running in the background
- somewhat simpler code and diagrams

same either way:
- how records are saved/persisted in the database
- how searches are run

### hypothetical a: django-shtrove in osf.io, still with bulk indexer

```mermaid
sequenceDiagram
    box OSF
    participant oq as queues (rabbitmq)
    participant ow as worker (celery)
    participant od as db (postgres)
    participant si as indexer
    participant se as elasticsearch
    end
    oq -->> ow: receive update task
    od <<-->> ow: gather metadata
    ow ->> od: save metadata to shtrove tables
    ow ->> oq: enqueue indexer message
    oq -->> si: bulk receive messages
    od <<-->> si: bulk load metadata records
    si ->> se: bulk update elastic indexes
```


### hypothetical b: install django-shtrove in osf.io, without bulk indexer

```mermaid
sequenceDiagram
    box OSF
    participant oq as queues (rabbitmq)
    participant ow as worker (celery)
    participant od as db (postgres)
    participant se as elasticsearch
    end
    oq -->> ow: receive update task
    od <<-->> ow: gather metadata
    ow ->> od: save metadata to shtrove tables
    ow ->> se: update elastic indexes
```
