#!/usr/bin/env python
# coding: utf-8
from __future__ import annotations

import os

import boto3

from dotenv import load_dotenv
from botocore.config import Config

def build_gcs_s3_client():
    load_dotenv()
    access_id = os.environ["GCS_ACCESS_KEY_ID"]
    secret = os.environ["GCS_SECRET_ACCESS_KEY"]

    return boto3.client(
        "s3",
        endpoint_url="https://storage.googleapis.com",
        aws_access_key_id=access_id,
        aws_secret_access_key=secret,
        region_name="auto",
        config=Config(signature_version="s3"),
    )


def parse_gcs_uri(uri: str) -> tuple[str, str]:
    """Split 'gs://bucket/some/key.ext' into ('bucket', 'some/key.ext')."""
    without_scheme=uri.removeprefix("gs://")
    bucket, _, key=without_scheme.partition("/")
    return bucket, key