#!/usr/bin/env python
# coding: utf-8

from __future__ import annotations

import duckdb

from pathlib import Path
from datetime import date

from src.processing.silver_layer import silver_layer

# code, product_name, generic_name, created_datetime, last_modified_datetime, countries_tags, brands, categories_tags, categories, main_category, completeness, quantity, product_quantity
# 
# '0001', 'Product A', NULL, TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2026-01-02 00:00:00', 'en:france', 'BrandA', 'en:dog-food', 'Dog food', 'dog-food', 0.8, '1kg', 1.0
# '0001', 'Product A (older)', NULL, TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2025-12-01 00:00:00', 'en:france', 'BrandA', 'en:dog-food', 'Dog food', 'dog-food', 0.5, '1kg', 1.0
# '0002', NULL, NULL, TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2026-01-01 00:00:00', 'en:germany', 'BrandB', 'en:cat-food', 'Cat food', 'cat-food', 0.6, '500g', 0.5
# NULL, 'No Code Product', NULL, TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2026-01-01 00:00:00', 'en:spain', 'BrandC', 'en:cat-food', 'Cat food', 'cat-food', 0.7, '2kg', 2.0
# 


def _write_sample_bronze(path: Path) -> None:
    con=duckdb.connect()
    con.execute(f"""
        COPY (
            SELECT * FROM (VALUES
                ('0001', 'Product A', NULL, TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2026-01-02 00:00:00', 'en:france', 'BrandA', 'en:dog-food', 'Dog food', 'dog-food', CAST(0.8 AS DOUBLE), '1kg', CAST(1.0 AS DOUBLE)),
                ('0001', 'Product A (older)', NULL, TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2025-12-01 00:00:00', 'en:france', 'BrandA', 'en:dog-food', 'Dog food', 'dog-food', CAST(0.5 AS DOUBLE), '1kg', CAST(1.0 AS DOUBLE)),
                ('0002', NULL, NULL, TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2026-01-01 00:00:00', 'en:germany', 'BrandB', 'en:cat-food', 'Cat food', 'cat-food', CAST(0.6 AS DOUBLE), '500g', CAST(0.5 AS DOUBLE)),
                (NULL, 'No Code Product', NULL, TIMESTAMP '2026-01-01 00:00:00', TIMESTAMP '2026-01-01 00:00:00', 'en:spain', 'BrandC', 'en:cat-food', 'Cat food', 'cat-food', CAST(0.7 AS DOUBLE), '2kg', CAST(2.0 AS DOUBLE))
            ) AS t(code, product_name, generic_name, created_datetime, last_modified_datetime, countries_tags, brands, categories_tags, categories, main_category, completeness, quantity, product_quantity)
        ) TO '{path}' (FORMAT PARQUET)
    """)
    con.close()


def test_silver_layer_drops_null_code_rows(tmp_path: Path) -> None:
    bronze_path=tmp_path / "test_bronze.parquet"
    _write_sample_bronze(bronze_path)

    dest_path=silver_layer(
        bronze_path=bronze_path,
        dest_dir=tmp_path / "test_silver",
        run_date=date(2026, 7, 1)
    )

    codes=duckdb.sql(f"SELECT code FROM '{dest_path}'").fetchall()

    assert None not in [c[0] for c in codes]


def test_silver_layer_drops_rows_with_no_usuable_name(tmp_path: Path) -> None:
    bronze_path=tmp_path / "test_bronze.parquet"
    _write_sample_bronze(bronze_path)

    dest_path=silver_layer(
        bronze_path=bronze_path,
        dest_dir=tmp_path / "test_silver",
        run_date=date(2026, 7, 1)
    )

    result=duckdb.sql(f"SELECT * FROM '{dest_path}' WHERE code='0002'").fetchall()

    assert result == []


def test_silver_layer_keeps_most_recent(tmp_path: Path) -> None:
    bronze_path=tmp_path / "test_bronze.parquet"
    _write_sample_bronze(bronze_path)

    dest_path=silver_layer(
        bronze_path=bronze_path,
        dest_dir=tmp_path / "test_silver",
        run_date=date(2026, 7, 1)
    )

    result=duckdb.sql(f"""
                SELECT
                    code, 
                    product_name, 
                    completeness
                FROM '{dest_path}' 
                WHERE code='0001'
            """).fetchall()

    assert len(result) == 1
    assert result[0] == ("0001", "Product A", 0.8)

def test_silver_layer_output_row_count(tmp_path: Path) -> None:
    bronze_path=tmp_path / "test_bronze.parquet"
    _write_sample_bronze(bronze_path)

    dest_path=silver_layer(
        bronze_path=bronze_path,
        dest_dir=tmp_path / "test_silver",
        run_date=date(2026, 7, 1)
    )

    result=duckdb.sql(f"SELECT COUNT(*) FROM '{dest_path}'").fetchone()

    assert result == (1, )