#!/usr/bin/env python
# coding: utf-8

from __future__ import annotations

import requests
import logging
import tempfile
import argparse

from pathlib import Path
from datetime import date

from src.common.gcs_s3 import build_gcs_s3_client, parse_gcs_uri

URL="https://static.openpetfoodfacts.org/data/en.openpetfoodfacts.org.products.csv.gz"
RAW_DIR="data/raw"
CHUNK_SIZE=8192

logger=logging.getLogger(__name__)


def downloader(
        url: str, 
        dest_dir: str, 
        run_date: date | None = None,
        gcs: bool = False
    ) -> str:

    run_date=run_date or date.today()

    response=requests.get(url, stream=True, timeout=30)
    response.raise_for_status()

    if gcs:
        dest_path=f"{dest_dir.rstrip('/')}/{run_date.isoformat()}/products.csv.gz"

        logger.info(
            "Starting download...",
            extra={"URL": url, "destination": dest_path})

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path=Path(tmp_dir) / "products.csv.gz"
            with open(tmp_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    f.write(chunk)

            bucket, key=parse_gcs_uri(dest_path)
            client=build_gcs_s3_client()
            client.upload_file(str(tmp_path), bucket, key)

        logger.info(
            "Download Complete!",
            extra={"destination": dest_path})
        
        return dest_path

    else:
        snap_dir=Path(dest_dir) / run_date.isoformat()
        snap_dir.mkdir(exist_ok=True, parents=True)

        fin_path=snap_dir / "products.csv.gz"

        logger.info(
            "Starting download...",
            extra={"URL": url, "destination": str(fin_path)})

        with open(fin_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)

        logger.info(
            "Download Complete!",
            extra={"destination": str(fin_path), "size_bytes": fin_path.stat().st_size})

        return str(fin_path)


def run() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    parser=argparse.ArgumentParser(description="Download dataset")
    parser.add_argument(
        "--dest-dir",
        type=str,
        default=RAW_DIR,
        help="Destination directory (local or gs://)"
    )
    parser.add_argument(
        "--gcs",
        action="store_true",
        help="Upload to GCS instead of local"
    )
    args=parser.parse_args()

    try:
        path=downloader(URL, args.dest_dir, gcs=args.gcs)
    except requests.HTTPError as exc:
        logger.error("Download failed...", extra={"error": str(exc)})
        raise SystemExit(1) from exc

    print(f"Saved Dataset to {path}")

if __name__ == "__main__":
    run()