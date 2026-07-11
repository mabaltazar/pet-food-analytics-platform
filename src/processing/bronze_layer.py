from __future__ import annotations

from pathlib import Path
from datetime import date

import logging
import duckdb
import argparse

logger = logging.getLogger(__name__)

def bronze_layer(csv_path: Path, dest_dir: Path, run_date: date | None = None) -> Path:

    run_date=run_date or date.today()
    snap_dir=dest_dir / run_date.isoformat()
    snap_dir.mkdir(parents=True, exist_ok=True)
    
    dest_path=snap_dir / "products.parquet"

    logger.info(
        "Starting bronze layer processing",
        extra={"csv_path": str(csv_path), "destination": str(dest_path)}
    )

    con = duckdb.connect()
    source=f"read_csv('{csv_path}', delim='\t', header=true, sample_size=-1)"

    con.execute(f"""
        COPY (SELECT * FROM {source})
        TO '{dest_path}' (FORMAT Parquet, COMPRESSION GZIP)
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
    parser.add_argument("csv_path", type=Path, help="Path to the input raw CSV file")
    args=parser.parse_args()

    dest_path=bronze_layer(args.csv_path, Path("data/bronze"))
    print(f"Saved bronze output to {dest_path}")

if __name__ == "__main__":
    main()