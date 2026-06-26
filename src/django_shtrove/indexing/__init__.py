"""
TODO:

- use entry-points to register/discover indexing strategy implementations
    - replace static share.search.index_strategy._AvailableStrategies
    - see https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/#using-package-metadata

- simplified base/abstract share.search.index_strategy.IndexStrategy:
    - (for more flexible interface allowing non-elastic strategies) consider removing
        IndexStrategy.SpecificIndex from abstract base class, let implementations handle
        multiple indexes as they will
    - (for less tangled import dependencies) consider using typing.Protocol instead of abc.ABC

- decide whether to keep indexer daemon
    - reasons to keep:
        - higher performance for bulk re-indexing, backfilling new indexes
        - more reliability for multiple indexing strategies in parallel
            (for each strategy, separate urgent/nonurgent queues and indexer threads)
        - avoids celery-worker logjams
    - reasons to remove:
        - simplify indexing strategies -- index only one item at a time
        - reduce amount of code to maintain (tho rarely requires attention since last rewrite)

if keeping indexer daemon, pull from:
    - share.search.daemon
    - share.search.messages
    - share.search.index_messenger
if removing indexer daemon:
    - replace `IndexStrategy.pls_handle_messages_chunk` with one-at-a-time method
    - index each item to each strategy in separate tasks/calls
    - be careful to handle errors robustly and avoid creating bottlenecks
"""
