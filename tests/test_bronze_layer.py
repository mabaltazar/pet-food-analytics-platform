from __future__ import annotations

import duckdb

from datetime import date
from pathlib import Path

from src.processing.bronze_layer import bronze_layer

def _write_sample_csv(path: Path) -> None:
    path.write_text(
        "code\tproduct_name\tcompleteness\n"
        "0001\tProduct A\t0.5\n"
        "0002\tProduct B\t0.8\n"
    )

def test_bronze_layer_preserve_row_and_column_count(tmp_path: Path) -> None:
    csv_path=tmp_path / "products.csv"
    _write_sample_csv(csv_path)

    dest_path=bronze_layer(
        csv_path=csv_path, 
        dest_dir=tmp_path / "bronze", 
        run_date=date(2026, 7, 1)
    )

    assert dest_path.exists()
    assert dest_path == tmp_path / "bronze" / "2026-07-01" / "products.parquet"

    result=duckdb.sql(f"SELECT * FROM read_parquet('{dest_path}')").fetchall()
    assert len(result) == 2

    columns=duckdb.sql(f"DESCRIBE SELECT * FROM read_parquet('{dest_path}')").fetchall()
    column_names=[col[0] for col in columns]
    assert column_names == ["code", "product_name", "completeness"]

def test_bronze_layer_preserves_all_values(tmp_path: Path) -> None:
    csv_path=tmp_path / "products.csv"
    _write_sample_csv(csv_path)

    dest_path=bronze_layer(
        csv_path=csv_path, 
        dest_dir=tmp_path / "bronze", 
        run_date=date(2026, 7, 1)
    )

    result=duckdb.sql(f"SELECT * FROM read_parquet('{dest_path}') ORDER BY code").fetchall()
    expected=[
        ("0001", "Product A", 0.5),
        ("0002", "Product B", 0.8),
    ]
    assert result == expected