# ADR 0003: BigQuery over DuckDB as the Warehouse

## Status
Accepted

## Context
DuckDB is a capable embedded warehouse and had already been used in an earlier, smaller project to learn dbt fundamentals. For this project, the choice was between continuing with DuckDB (zero infrastructure, fast local iteration) or moving to BigQuery (cloud-native, supports partitioning/clustering at scale, but requires GCP setup and has usage costs).

Since the project's data lake layer already moved to GCS (ADR 0002), keeping the warehouse local in DuckDB would create an awkward split between a cloud lake and a local warehouse, and would not demonstrate experience with a production-scale cloud warehouse.

## Decision
Use BigQuery as the data warehouse, with tables partitioned and clustered based on expected query patterns (date-range filters, category grouping).

## Consequences
- Demonstrates cloud data warehouse design (partitioning/clustering)rather than repeating a previously-used tool.
- Introduces BigQuery cost-awareness (query bytes scanned, storage) as an ongoing development concern, unlike DuckDB's zero-cost local operation.
- Keeps the lake (GCS) and warehouse (BigQuery) in the same cloud ecosystem, simplifying the load step between them.