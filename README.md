# Pet Food Analytics Platform

## Status: 🚧 In Progress

## Overview
An end-to-end batch data pipeline that ingests the Open Pet Food Facts
dataset, processes it through a layered data lake, loads it into a cloud
data warehouse, transforms it into analytics-ready tables, and serves
the results through a dashboard.

Current snapshot: 15,145 products, 210 source columns (profiled and
reduced to a smaller analytical schema — see `docs/specs/silver_transform.md`).

## Architecture
See `docs/architecture.md` for the full pipeline diagram and layer breakdown.

## Tech Stack
- Language: Python (uv)
- Data Lake: GCS
- Warehouse: BigQuery
- Transformations: dbt
- Orchestration: TBD (Kestra or Prefect)
- Dashboard: TBD
- IaC: Terraform

## Project Structure
- data/          # raw / bronze / silver (gitignored, dated snapshots)
- src/
- ingestion/     # download.py
- processing/    # data_profile.py / bronze_layer.py / silver_layer.py
- tests/         # test_download.py / test_bronze_layer.py / test_silver_layer.py
- docs/
- adr/           # architecture decision records
- specs/         # transformation specs (rules, reasoning, success criteria)
- architecture.md
- data_dictionary.md

## Setup & Reproduction
_TBD_

## Progress Checklist
- [x] Repo initialized
- [x] Raw data ingestion (`download.py`, tested)
- [x] Data profiling (`profile.py`, run against real data)
- [x] Bronze layer (`bronze_layer.py`, tested — format conversion, all columns preserved)
- [x] Silver layer (`silver_layer.py`, tested — column selection, null filtering, dedup, UTC normalization)
- [ ] Terraform: GCS bucket + BigQuery datasets
- [ ] Load silver -> BigQuery
- [ ] dbt staging + marts (incl. countries_tags unnesting, date truncation)
- [ ] Orchestration (Kestra)
- [ ] Dashboard (Streamlit)
- [ ] CI (GitHub Actions)

## Key Design Decisions
See `docs/adr/` for full reasoning behind each major choice:
- [001 — Batch over streaming](docs/adr/001-batch-over-streaming.md)
- [002 — Cloud (GCP) over local-first](docs/adr/002-cloud-over-local.md)
- [003 — BigQuery over DuckDB as warehouse](docs/adr/003-bigquery-over-duckdb.md)
- [004 — DuckDB for local profiling](docs/adr/004-duckdb-for-profiling.md)
- [005 — Silver layer grain: one row per product](docs/adr/005-one-row-per-product.md)
- [006 — Bronze/Silver Layer definition](docs/adr/006-bronze-silver-definition.md)