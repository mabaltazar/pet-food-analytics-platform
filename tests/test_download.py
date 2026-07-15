#!/usr/bin/env python
# coding: utf-8

from __future__ import annotations
from unittest.mock import MagicMock

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


def test_downloader_gcs_uploads_and_returns_gs_path(tmp_path: Path, mocker) -> None:
    fake_response=FakeResponse(chunks=[b"col1,col2\n", b"val1,val2\n"])
    mocker.patch("src.ingestion.download.requests.get", return_value=fake_response)

    fake_client=MagicMock()
    captured={}

    def fake_upload_file(filename, bucket, key):
        captured["content"]=Path(filename).read_bytes()
        captured["bucket"]=bucket
        captured["key"]=key

    fake_client.upload_file.side_effect = fake_upload_file
    mocker.patch("src.ingestion.download.build_gcs_s3_client", return_value=fake_client)

    result_path=downloader(
        url="https://example.com/data.csv.gz",
        dest_dir="gs://fake-bucket/raw",
        run_date=date(2026, 7, 1),
        gcs=True,
    )

    assert result_path == "gs://fake-bucket/raw/2026-07-01/products.csv.gz"
    assert captured["bucket"] == "fake-bucket"
    assert captured["key"] == "raw/2026-07-01/products.csv.gz"
    assert captured["content"] == b"col1,col2\nval1,val2\n"
    
    fake_client.upload_file.assert_called_once()

def test_downloader_writes_file_to_folder(tmp_path: Path, mocker) -> None:
    fake_response=FakeResponse(chunks=[b"col1,col2\n", b"val1,val2\n"])
    mocker.patch("src.ingestion.download.requests.get", return_value=fake_response)

    result_path=downloader(
        url="https://example.com/data.csv.gz",
        dest_dir=str(tmp_path),
        run_date=date(2026, 7, 1),
    )

    assert result_path == str(tmp_path / "2026-07-01" / "products.csv.gz")
    assert Path(result_path).exists()
    assert Path(result_path).read_bytes() == b"col1,col2\nval1,val2\n"


def test_downloader_defaults_to_today(tmp_path: Path, mocker) -> None:
    fake_response=FakeResponse(chunks=[b"data"])
    mocker.patch("src.ingestion.download.requests.get", return_value=fake_response)

    result_path=downloader(
        url="https://example.com/data.csv.gz",
        dest_dir=str(tmp_path),
    )

    assert Path(result_path).parent.name == date.today().isoformat()

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

    assert Path(result_path).exists()