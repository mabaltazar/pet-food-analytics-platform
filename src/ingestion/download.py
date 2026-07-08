#!/usr/bin/env python
# coding: utf-8

from __future__ import annotations

import requests
import logging

from pathlib import Path
from datetime import date

URL="https://static.openpetfoodfacts.org/data/en.openpetfoodfacts.org.products.csv.gz"
RAW_DIR=Path("data/raw")
CHUNK_SIZE=8192

logger=logging.getLogger(__name__)


def downloader(url: str, dest_dir: Path, run_date: date | None = None) -> Path:

    run_date=run_date or date.today()
    snap_dir=dest_dir / run_date.isoformat()
    snap_dir.mkdir(exist_ok=True, parents=True)

    fin_path=snap_dir / "products.csv.gz"

    logger.info("Starting download...",extra={"URL": url, "destination": str(fin_path)})

    response=requests.get(url, stream=True, timeout=30)
    response.raise_for_status()

    with open(fin_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            f.write(chunk)

    logger.info("Download Complete!",extra={"destination": str(fin_path), "size_bytes": fin_path.stat().st_size})

    return fin_path


def run() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    try:
        path=downloader(URL, RAW_DIR)
    except requests.HTTPError as exc:
        logger.error("Download failed...", extra={"error": str(exc)})
        raise SystemExit(1) from exc

    print(f"Saved Dataset to {path}")

if __name__ == "__main__":
    run()