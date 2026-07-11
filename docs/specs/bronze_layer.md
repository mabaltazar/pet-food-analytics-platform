# Bronze Layer Spec: Pet Food Products
**Status: Finalized**

## Purpose
Convert raw data into a more efficient, typed format (Parquet) with
zero row or column filtering. Bronze is a faithful, complete copy of
the source — a safety net that lets later layers be rebuilt without
re-running ingestion, even if requirements change.

## Input
- Source: raw/{date}/products.csv.gz (tab-delimited, 210 columns)

## Rules
1. Convert all columns as-is (SELECT *) to Parquet format.
2. No column pruning, no row filtering, no deduplication — see
   docs/specs/silver_transform.md for all curation logic.
3. Types are inferred by DuckDB (sample_size=-1, full-file scan) rather
   than explicitly cast, since inference has been confirmed correct for
   all columns checked so far (see docs/data_dictionary.md).

## Success Criteria
- Output contains all 210 source columns.
- Row count matches input row count exactly (15,145, current snapshot).
- File is valid, readable Parquet.

## Out of scope for this layer
- Column selection (silver)
- Deduplication (silver)
- Null-based row filtering (silver)
- Multi-value field unnesting (dbt marts)