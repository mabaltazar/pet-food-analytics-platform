# Data Dictionary — Pet Food Products (Silver Layer)

Based on profiling of the current snapshot (15,145 rows, 210 source columns).
Full reasoning in `docs/specs/silver_transform.md`.

## Retained columns

| Column | Type | Null rate | Notes |
|---|---|---|---|
| `code` | VARCHAR | 0% | Barcode, unique per product. Primary key. |
| `product_name` | VARCHAR | 19.7% | |
| `generic_name` | VARCHAR | 92.3% | Rarely populated; used with product_name for a combined not-null rule. |
| `created_datetime` | TIMESTAMP | 0% | Used for dashboard's temporal tile. |
| `last_modified_datetime` | TIMESTAMP | 0% | Used for dedup logic (defensive; no dupes in current snapshot). |
| `countries_tags` | VARCHAR | 1.6% | Comma-separated multi-value; unnested only in dbt marts. |
| `brands` | VARCHAR | 54.9% | High cardinality (2,070); needs top-N grouping if visualized. |
| `categories_tags` / `categories` / `main_category` | VARCHAR | 63-69% | High cardinality; needs top-N grouping if visualized. |
| `completeness` | DOUBLE | 0% | Numeric score, observed range 0.05-1.0875 (max >1.0 unexplained — open item). Candidate quality filter. |
| `quantity` / `product_quantity` | VARCHAR/DOUBLE | 53-60% | |

## Dropped columns

| Column | Reason |
|---|---|
| `nova_group` | 94.4% null, not designed for pet food. |
| `nutriscore_grade`, `nutriscore_score` | Only 145/15,145 (0.96%) have a real grade once `'unknown'`/`'not-applicable'` placeholders are excluded. |
| `environmental_score_grade`, `environmental_score_score` | Only 50/15,145 (0.33%) real values once placeholders excluded. |
| `pnns_groups_1`, `pnns_groups_2` | Only 79/15,145 (0.52%) real values once placeholders excluded. |
| `cities` | 100% null. |
| `states` | Fully populated but contains Open Food Facts internal workflow tags, not a product attribute. |
| `brand_owner` | 99.7% null, only 1 distinct value among non-null rows. |

## Known data conventions
- This schema uses `'unknown'` and `'not-applicable'` as string placeholders
  in several categorical/grade fields, rather than true SQL NULL. Raw
  null-rate counts on these fields are misleading; always check actual
  value distributions before trusting a column's apparent population rate.
- Several `_tags`-suffixed fields (e.g. `countries_tags`) store multiple
  values as a single comma-separated string per row.