# ADR 0005: Keep Silver Layer at One-Row-Per-Product Grain

## Status
Accepted

## Context
Profiling confirmed that several fields (`countries_tags`, and likely
`categories_tags`/`brands` similarly) contain comma-separated multi-value
strings — e.g. a single product sold in multiple countries is stored as
one row with `countries_tags = "en:france,en:italy,en:spain"`, rather
than one row per product-country combination.

The dashboard's categorical tile requires counting products per country,
which means these multi-value strings need to be split ("unnested") so
each country is counted individually. Two options existed for where
this unnesting happens:
1. At the silver layer itself, changing silver's grain from one row per
   product to one row per product-country pair.
2. Only within the specific dbt mart that powers the dashboard, leaving
   silver at one row per product.

## Decision
Keep the silver layer at one-row-per-product grain. Perform unnesting
of multi-value fields (starting with `countries_tags`) only within the
dbt mart(s) that specifically require it.

## Consequences
- Any table or query built directly on silver can assume one row per
  product, with no risk of double-counting from an unnest operation
  happening upstream.
- The mart layer takes on responsibility for handling multi-value
  fields correctly (via UNNEST/string_split), which is the appropriate
  place for it since it's the layer that's actually opinionated about
  how the data will be visualized.
- If a future mart needs a different unnesting of the same field (e.g.
  a different grouping granularity), it can do so independently without
  affecting silver or other marts.