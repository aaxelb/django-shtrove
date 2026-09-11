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

## hypothetical a: install django-shtrove in osf.io, still with bulk indexer

```mermaid
sequenceDiagram
    box OSF
    participant oq as queues (rabbitmq)
    participant od as db (postgres)
    participant ow as worker (celery)
    participant si as indexer
    participant se as elasticsearch
    end
    oq -->> ow: receive update task
    od <<-->> ow: gather metadata
    ow ->> od: save gathered metadata to shtrove record
    ow ->> od: save derived cards
    ow ->> oq: enqueue indexer message
    oq -->> si: bulk receive messages
    od <<-->> si: bulk load metadata records
    si ->> se: bulk index
```
benefits:
- less contention with other tasks over celery workers/queues
- faster/cheaper indexing of many records in a row, with fewer database queries

costs:
- some code complexity
- additional daemon process always running


## hypothetical b: install django-shtrove in osf.io, without bulk indexer

```mermaid
sequenceDiagram
    box OSF
    participant oq as queues (rabbitmq)
    participant od as db (postgres)
    participant ow as worker (celery)
    participant se as elasticsearch
    end
    oq -->> ow: receive update task
    od <<-->> ow: gather metadata
    ow ->> od: save gathered metadata to shtrove record
    ow ->> od: save derived cards
    ow ->> se: bulk index
```
benefits:
- simpler diagram, less code

costs:
- more contention with other tasks over celery workers/queues
- slower/costlier indexing of many records at once
