# ADR 0001: Batch Processing over Streaming

## Status
Accepted

## Context
The chosen dataset, Open Pet Food Facts, is distributed as a periodic snapshot export (a single .csv.gz file updated on a schedule by the source), not as a real-time event feed.

## Decision
Use batch processing, with a daily (or similar interval) scheduled ingestion
job rather than a streaming consumer/producer architecture.

## Consequences
- Simpler pipeline: no Kafka/Pulsar/Kinesis infrastructure needed.
- Matches how this data would realistically be processed in production, since the source itself only publishes periodic snapshots — there is no underlying event stream to consume.
- Re-ingesting the full file on each run means designing for idempotency