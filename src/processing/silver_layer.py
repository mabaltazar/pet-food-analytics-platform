#!/usr/bin/env python
# coding: utf-8
from __future__ import annotations
from pathlib import Path
from datetime import date

import duckdb
import logging
import argparse

from src.common.duckdb_gcs import configure_gcs

logger = logging.getLogger(__name__)


def silver_layer(
        bronze_path: str, 
        dest_dir: str, 
        run_date: date | None = None,
        gcs: bool = False
        ) -> str:
    
    run_date=run_date or date.today()
    
    if gcs:
        snap_dir=f"{dest_dir.rstrip('/')}/{run_date.isoformat()}"
        dest_path=f"{snap_dir}/products.parquet"
    else:
        snap_dir=Path(dest_dir) / run_date.isoformat()
        snap_dir.mkdir(parents=True, exist_ok=True)
        dest_path=str(snap_dir / "products.parquet")

    logger.info(
        f"Starting silver layer",
        extra={"bronze_path": str(bronze_path), "destination": str(dest_path)}
    )

    con=duckdb.connect()

    if gcs:
        configure_gcs(con)

    con.execute(f"""
        COPY (
                SELECT 
                    code, 
                    product_name, 
                    generic_name, 
                    created_datetime, 
                    last_modified_datetime,
                    countries_tags, 
                    brands, 
                    categories_tags, 
                    categories, 
                    main_category, 
                    completeness, 
                    quantity, 
                    product_quantity
                FROM (
                    SELECT 
                        code, 
                        product_name, 
                        generic_name, 
                        created_datetime AT TIME ZONE 'UTC' AS created_datetime,
                        last_modified_datetime AT TIME ZONE 'UTC' AS last_modified_datetime,
                        countries_tags, 
                        brands, 
                        categories_tags, 
                        categories,
                        main_category, 
                        completeness, 
                        quantity, 
                        product_quantity,
                            ROW_NUMBER() OVER (
                                PARTITION BY code
                                ORDER BY last_modified_datetime DESC
                            ) AS rn
                    FROM '{bronze_path}'
                    WHERE code IS NOT NULL
                      AND NOT (product_name IS NULL AND generic_name IS NULL)
                )
                WHERE rn = 1
        )   TO '{dest_path}' (FORMAT PARQUET)
    """)
    
    con.close()

    logger.info(
        "Silver layer completed!",
        extra={"destination": str(dest_path)}
    )

    return dest_path

def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        )
    
    parser=argparse.ArgumentParser(description="Silver layer processing")
    parser.add_argument("bronze_path", type=str, help="Path to the bronze layer parquet file")
    parser.add_argument(
        "--dest-dir",
        type=str,
        default="data/silver",
        help="Destination directory for the silver layer output"
    )
    parser.add_argument(
        "--gcs",
        action="store_true",
        help="Use GCS for data storage"
    )

    args=parser.parse_args()

    dest_path=silver_layer(args.bronze_path, args.dest_dir, gcs=args.gcs)
    print(f"Saved silver output to {dest_path}")

if __name__ == "__main__":
    main()

