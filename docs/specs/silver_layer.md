# Silver Layer Spec: Pet Food Products
**Status: Finalized against real profiling data (15,145 rows, 210 columns)**

## Purpose
Transform bronze-layer data into a deduplicated, validated dataset ready
for warehouse loading.

## Input
- Source: bronze/{date}/products.parquet
- Row count (current snapshot): 15,145 products

## Columns to drop
The following columns were profiled and confirmed too sparse or not
analytically meaningful to carry into silver:

- `nova_group`, `nutriscore_grade`, `nutriscore_score`,
  `environmental_score_grade`, `environmental_score_score`,
  `pnns_groups_1`, `pnns_groups_2` — all use `'unknown'`/`'not-applicable'`
  as placeholder values rather than true NULL, masking true sparsity.
  Real usable population in each case is under 1% of rows once
  placeholders are excluded (e.g. nutriscore_grade: 145/15,145 real
  grades; environmental_score_grade: 50/15,145; pnns_groups_1: 79/15,145).
- `cities` — 100% null, no data at all.
- `states` — fully populated but contains Open Food Facts' internal
  data-entry workflow tags (e.g. "to-be-completed", "photos-uploaded"),
  not a product attribute. Not useful for product analytics.
- `brand_owner` — 99.7% null and only 1 distinct value among the
  non-null rows; effectively constant/unused.

## Columns to keep as-is
- `code` — 0% null, 100% unique. Natural primary key.
- `created_datetime`, `last_modified_datetime` — 0% null. Used for the
  dashboard's temporal tile.
- `completeness` — 0% null, numeric (observed range 0.05-1.0875,
  average 0.325). Candidate as a data-quality filter threshold, not yet
  finalized (values above 1.0 observed and not yet explained; treat as
  a known open item, not a blocker).
- `product_name` — 19.7% null. Used together with `generic_name` in the
  null-name rule below.

## Columns to keep with transformation needed
- `countries_tags` — 1.6% null, but contains comma-separated multi-value
  strings (e.g. "en:france,en:italy,en:spain") for products sold in
  multiple countries. Left as one-row-per-product in silver; unnesting
  into one-row-per-product-country happens only in the dbt mart that
  powers the dashboard's categorical tile (see ADR 0006).
- `brands`, `categories_tags` / `categories` / `main_category` — moderate
  sparsity (55-69% null) and high cardinality (700-2,000+ distinct
  values). Usable, but any dashboard/mart use requires top-N grouping
  with an "Other" bucket, similar to the countries approach.

## Rules
1. Drop rows where `code` is null. (Currently a no-op: profiling
   confirmed 0 null values in the current snapshot; kept as a
   defensive rule for future snapshots.)
2. Deduplicate on `code`, keeping the row with the most recent
   `last_modified_datetime`. (Currently a no-op: profiling confirmed
   0 duplicate `code` values in the current snapshot; kept defensively.)
3. Drop the columns listed under "Columns to drop" above.
4. Reject rows where `product_name` is null AND `generic_name` is null.
   Confirmed: 2,978 of 15,145 rows (19.7%) meet this condition and
   would be dropped.
5. Treat `'unknown'` and `'not-applicable'` as equivalent to NULL when
   evaluating any retained categorical/grade column — do not count
   them as "populated" in downstream data quality tests.
6. Leave `countries_tags`, `brands`, `categories_tags` un-split in
   silver; defer unnesting/top-N grouping to the dbt mart layer that
   consumes them (see ADR 0006: keep silver at one-row-per-product).

## Success Criteria
- Output row count matches input row count minus only rows dropped by
  rule 1 and rule 4 (rule 2 currently removes 0 rows; rule 3 removes
  columns, not rows).
- No duplicate `code` values in output.
- No columns from the "Columns to drop" list present in the output schema.
- All rows have non-null `code` and at least one of `product_name` /
  `generic_name`.

## Open items
- Confirm and document the cause of `completeness` values exceeding 1.0
  (observed max: 1.0875) — treat as a known upstream data quirk unless
  investigation shows otherwise.

## Known limitations (not addressed)
- Brand names (`brands`), and likely `categories`/`main_category`, contain
  casing and formatting inconsistencies (e.g. "purina" vs "Purina",
  "Hills Science diet" vs "Hill's Science Diet"). Confirmed via spot-check
  during profiling. Not addressed in this version — would require either
  simple normalization (casing/whitespace only, which would not resolve
  punctuation differences like the apostrophe example) or a full brand
  name mapping/entity-resolution effort, judged out of scope for this
  project's current goals.