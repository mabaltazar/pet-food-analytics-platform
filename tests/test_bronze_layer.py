from __future__ import annotations
from unittest.mock import patch, MagicMock

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

def test_bronze_layer_builds_gcs_path_and_calls_configure_gcs(tmp_path: Path) -> None:
    fake_con=MagicMock()

    with patch("src.processing.bronze_layer.duckdb.connect", return_value=fake_con), \
            patch("src.processing.bronze_layer.configure_gcs") as mock_configure_gcs:

        dest_path=bronze_layer(
            csv_path="gs://fake-bucket/raw/2026-07-01/products.csv",
            dest_dir="gs://fake-bucket/bronze",
            run_date=date(2026, 7, 1),
            gcs=True
        )

    assert dest_path == "gs://fake-bucket/bronze/2026-07-01/products.parquet"
    mock_configure_gcs.assert_called_once_with(fake_con)
    fake_con.close.assert_called_once()

def test_bronze_layer_preserve_row_and_column_count(tmp_path: Path) -> None:
    csv_path=tmp_path / "products.csv"
    _write_sample_csv(csv_path)

    dest_path=bronze_layer(
        csv_path=str(csv_path), 
        dest_dir=str(tmp_path / "bronze"), 
        run_date=date(2026, 7, 1)
    )

    assert Path(dest_path).exists()
    assert dest_path == str(tmp_path / "bronze" / "2026-07-01" / "products.parquet")

    result=duckdb.sql(f"SELECT * FROM read_parquet('{dest_path}')").fetchall()
    assert len(result) == 2

    columns=duckdb.sql(f"DESCRIBE SELECT * FROM read_parquet('{dest_path}')").fetchall()
    column_names=[col[0] for col in columns]
    assert column_names == ["code", "product_name", "completeness"]

def test_bronze_layer_preserves_all_values(tmp_path: Path) -> None:
    csv_path=tmp_path / "products.csv"
    _write_sample_csv(csv_path)

    dest_path=bronze_layer(
        csv_path=str(csv_path), 
        dest_dir=str(tmp_path / "bronze"), 
        run_date=date(2026, 7, 1)
    )

    result=duckdb.sql(f"SELECT * FROM read_parquet('{dest_path}') ORDER BY code").fetchall()
    expected=[
        ("0001", "Product A", 0.5),
        ("0002", "Product B", 0.8),
    ]
    assert result == expected