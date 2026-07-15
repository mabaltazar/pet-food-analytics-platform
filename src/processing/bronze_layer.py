from __future__ import annotations

from pathlib import Path
from datetime import date

import logging
import duckdb
import argparse

from src.common.duckdb_gcs import configure_gcs

logger = logging.getLogger(__name__)

def bronze_layer(
        csv_path: str, 
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
        "Starting bronze layer processing",
        extra={"csv_path": str(csv_path), "destination": str(dest_path)}
    )

    con=duckdb.connect()

    if gcs:
        configure_gcs(con)

    source=f"read_csv('{csv_path}', delim='\t', header=true, sample_size=-1)"

    con.execute(f"""
        COPY (SELECT * FROM {source})
        TO '{dest_path}' (FORMAT PARQUET)
    """)

    con.close()

    logger.info(
        "Bronze layer processing completed",
        extra={"destination": str(dest_path)}
    )
    return dest_path

def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    parser=argparse.ArgumentParser(description="Convert CSV to Parquet and store in bronze layer")
    parser.add_argument("csv_path", type=str, help="Path to the input raw CSV file")
    parser.add_argument(
        "--dest-dir",
        type=str,
        default="data/bronze",
        help="Destination directory for bronze output"
    )
    parser.add_argument(
        "--gcs",
        action="store_true",
        help="Treat dest_dir as a gs:// destination (skips local mkdir, configures GCS secret)"
    )

    args=parser.parse_args()

    dest_path=bronze_layer(args.csv_path, args.dest_dir, gcs=args.gcs)
    print(f"Saved bronze output to {dest_path}")

if __name__ == "__main__":
    main()