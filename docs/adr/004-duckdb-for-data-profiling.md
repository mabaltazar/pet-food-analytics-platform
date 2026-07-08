# ADR 0004: DuckDB for Local Profiling, Not as the Warehouse

## Status
Accepted

## Context
The raw dataset has 200+ columns and ships as a ~0.9GB compressed
(~9GB uncompressed) tab-delimited file. Before deciding which columns to
carry into the Bronze/Silver/Gold layers, the columns needed to be
inspected for type, null rate, and cardinality.

Loading the full file into a pandas DataFrame for this exploratory step
was judged impractical on a typical development machine given the
uncompressed size. Two realistic options existed: chunked pandas reads,
or DuckDB queried directly against the compressed file.

## Decision
Use DuckDB for the one-off profiling step, querying the .csv.gz file
directly via `read_csv(..., delim='\t')` without a separate decompression
step. Profile a fixed-size sample (default 500,000 rows) by default, with
a `--full` flag to scan the entire file once the column shortlist is
finalized.

This is a separate decision from ADR 0003: DuckDB is used here purely as
a local, embedded query engine for exploratory profiling, not as the
project's data warehouse (BigQuery fills that role).

## Consequences
- No manual decompression code needed; DuckDB handles gzip transparently.
- Profiling avoids loading the full ~9GB file into memory.
- Sampling introduces a small accuracy tradeoff on null-rate/cardinality
  estimates versus a full scan, judged acceptable for an initial
  column-shortlisting pass.
- The profiling script is treated as one-off tooling rather than a
  recurring pipeline stage, and is not covered by the same testing
  expectations as ingestion/processing code that runs unattended.