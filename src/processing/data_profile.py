from __future__ import annotations

import json
import logging
from pathlib import Path

import duckdb
import argparse

logger=logging.getLogger(__name__)

DEFAULT_OUTPUT_PATH=Path("data/bronze/profile_report.json")


def profile_dataset(csv_path: Path) -> list[dict]:

    con=duckdb.connect()
    source=f"read_csv('{csv_path}', delim='\t', header=true, sample_size=-1)"
    
    logger.info(
        "Starting profiling",
        extra={"csv_path": str(csv_path)},
    )
    
    columns=con.execute(
        f"DESCRIBE SELECT * FROM {source}"
    ).fetchall()

    profile: list[dict] = []
    for col_name, col_type, *_ in columns:
        row=con.execute(
            f"""
            SELECT
                COUNT(*) AS total_rows,
                COUNT("{col_name}") AS non_null_rows,
                COUNT(DISTINCT "{col_name}") AS distinct_values
            FROM {source}
            """
        ).fetchone()
        total_rows, non_null_rows, distinct_values = row
        null_rate= 1-(non_null_rows / total_rows) if total_rows else None

        profile.append(
            {
                "column": col_name,
                "type": col_type,
                "null_rate": round(null_rate, 4) if null_rate is not None else None,
                "distinct_values": distinct_values,
            }
        )

    con.close()
    logger.info(
        "Profiling complete", 
        extra={"columns_profiled": len(profile)}
    )
    return profile


def save_profile(profile: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(profile, indent=2))
    logger.info(
        "Profile report saved", 
        extra={"output_path": str(output_path)}
    )


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    parser=argparse.ArgumentParser(description="Profile the raw pet food dataset.")
    parser.add_argument("csv_path", type=Path, help="Path to raw products.csv.gz")
    args=parser.parse_args()

    profile=profile_dataset(args.csv_path)
    save_profile(profile, DEFAULT_OUTPUT_PATH)

if __name__ == "__main__":
    main()