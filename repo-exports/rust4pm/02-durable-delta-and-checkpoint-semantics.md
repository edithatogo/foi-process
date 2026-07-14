# Explore durable OCEL delta/checkpoint semantics

Design a generic companion abstraction for transactional/durable appends, checkpoints, revision/retraction conventions, and crash recovery. Do not replace `AppendableOCEL`; layer durability around it. Exit with benchmarks and at least two storage implementations or one implementation plus a fully generic trait test suite.
