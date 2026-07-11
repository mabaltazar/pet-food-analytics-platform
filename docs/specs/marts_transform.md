## Known deferred work from earlier layers
- Unnest `countries_tags` (comma-separated multi-value) — deferred from
  silver per ADR 0006, to be handled in the dbt mart powering the
  categorical dashboard tile.
- Truncate `last_modified_datetime` (or `created_datetime`) to date-level
  granularity for the temporal dashboard tile — full timestamp precision
  is preserved in silver for dedup correctness, but the dashboard chart
  needs day/week/month granularity.
- Same top-N + "Other" grouping treatment likely needed for `brands` and
  `categories_tags` as for `countries_tags`, given similarly high cardinality.
- Known limitation, not addressed: brand name casing/punctuation
  inconsistencies (e.g. "purina" vs "Purina", "Hills Science diet" vs
  "Hill's Science Diet") — see silver spec's "Known limitations" section.