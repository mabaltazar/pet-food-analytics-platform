#!/usr/bin/env python
# coding: utf-8

from __future__ import annotations

import pytest
import requests

from datetime import date
from pathlib import Path

from src.ingestion.download import downloader


class FakeResponse:
    def __init__(self, chunks: list[bytes], status_code: int=200) -> None:
        self._chunks=chunks
        self.status_code=status_code

    def iter_content(self, chunk_size: int):
        yield from self._chunks

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")


def test_downloader_writes_file_to_folder(tmp_path: Path, mocker) -> None:
    fake_response=FakeResponse(chunks=[b"col1,col2\n", b"val1,val2\n"])
    mocker.patch("src.ingestion.download.requests.get", return_value=fake_response)

    result_path=downloader(
        url="https://example.com/data.csv.gz",
        dest_dir=tmp_path,
        run_date=date(2026, 7, 1),
    )

    assert result_path == tmp_path / "2026-07-01" / "products.csv.gz"
    assert result_path.exists()
    assert result_path.read_bytes() == b"col1,col2\nval1,val2\n"


def test_downloader_defaults_to_today(tmp_path: Path, mocker) -> None:
    fake_response=FakeResponse(chunks=[b"data"])
    mocker.patch("src.ingestion.download.requests.get", return_value=fake_response)

    result_path=downloader(
        url="https://example.com/data.csv.gz",
        dest_dir=tmp_path,
    )

    assert result_path.parent.name == date.today().isoformat()

def test_downloader_raises_on_http_error(tmp_path: Path, mocker) -> None:
    fake_response=FakeResponse(chunks=[], status_code=404)
    mocker.patch("src.ingestion.download.requests.get", return_value=fake_response)

    with pytest.raises(requests.HTTPError):
        downloader(
            url="https://example.com/missing.csv.gz",
            dest_dir=tmp_path,
        )
    
def test_downloader_creates_missing_parent_dirs(tmp_path: Path, mocker) -> None:
    fake_response=FakeResponse(chunks=[b"data"])
    mocker.patch("src.ingestion.download.requests.get", return_value=fake_response)

    nested_dest=tmp_path / "does" / "not" / "exist" / "yet"
    result_path=downloader(
        url="https://example.com/data.csv.gz",
        dest_dir=nested_dest,
    )

    assert result_path.exists()




