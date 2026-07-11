# ADR 0006: Bronze/Silver Layer Definitions for This Project

## Status
Accepted

## Context
Medallion architecture terminology ("bronze," "silver," "gold") is not
strictly standardized across the industry — different teams draw the
line between layers differently. A common convention (popularized by
Databricks) defines bronze as raw data with minimal transformation
(format conversion only, all columns retained), and silver as cleaned,
column-pruned, deduplicated, validated data.

An earlier version of this pipeline's bronze layer performed column
selection (reducing 210 source columns to 13), which blurred bronze
and silver's responsibilities and removed the safety net of being able
to revisit dropped columns without re-running ingestion from raw.

## Decision
Adopt the following definitions for this project:
- `raw/`: untouched source snapshot (.csv.gz), exactly as downloaded.
- `bronze/`: format-converted (Parquet), all 210 source columns retained,
  types inferred but not pruned or filtered.
- `silver/`: column-pruned (see docs/specs/silver_transform.md),
  deduplicated, null-validated, analysis-ready.

## Consequences
- If dashboard or analysis requirements change and a previously-dropped
  column is needed, it can be recovered from bronze without re-running
  ingestion from raw.
- Bronze remains a faithful, complete copy of the source in a more
  efficient format (Parquet vs. CSV), consistent with common medallion
  architecture convention.
- Silver takes on both column-selection and row-level validation
  responsibilities, since both are "curation" decisions specific to
  this project's analytical needs.