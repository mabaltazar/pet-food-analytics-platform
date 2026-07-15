# ADR 0007: Hybrid Local/GCS Destination Pattern for Pipeline Scripts

## Status
Accepted

## Context
`download.py`, `bronze_layer.py`, and `silver_layer.py` originally only
wrote to local disk. Once Kestra orchestration begins, pipeline stages
will likely run in separate containers, meaning local disk cannot be
relied on as the handoff mechanism between stages — GCS needs to be the
real handoff point. At the same time, local paths remain valuable for
fast dev iteration and the existing local pytest test suite.

Two options were considered for how each script decides where to write:
1. Auto-detect from the destination string itself (e.g. a `gs://` prefix
   implies cloud, anything else implies local).
2. An explicit `--gcs` CLI flag (and corresponding `gcs: bool` function
   parameter), in addition to the destination string.

## Decision
Use an explicit `--gcs` flag/parameter rather than string-prefix
auto-detection. Each script's core function (`downloader`, `bronze_layer`,
`silver_layer`) accepts `dest_dir: str` and `gcs: bool = False`; when
`gcs=True`, the function builds a `gs://` path string and calls GCS-specific
setup (`configure_gcs()` for DuckDB-based scripts, a `boto3` client for
`download.py`), skipping local-only operations like `Path.mkdir()`.

## Consequences
- Callers state their intent explicitly rather than relying on Kestra (or
  a developer) to pass a correctly-prefixed string — reduces the chance
  of a silent local/cloud mismatch going unnoticed.
- All three scripts' `dest_dir`/return types changed from `Path` to `str`,
  since GCS URIs are not real filesystem paths — this required minor
  updates to existing tests that had asserted `Path`-specific behavior
  (`.exists()`, direct `Path` equality).
- `download.py` required a distinct GCS upload mechanism (`boto3` against
  GCS's S3-interoperability endpoint, reusing the same HMAC keys already
  used by `configure_gcs()`) since it does not use DuckDB and has no
  native `gs://` write path of its own — see `src/common/gcs_s3.py`.
- Adds one new dependency (`boto3`) and one new small helper module,
  but avoids introducing a second GCS credential type (e.g. a service
  account JSON), keeping one consistent auth mechanism across the
  pipeline for now.