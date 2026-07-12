#!/usr/bin/env python
# coding: utf-8

from __future__ import annotations

import os
import duckdb

from dotenv import load_dotenv

def configure_gcs(con: duckdb.DuckDBPyConnection) -> None:
    
    
    load_dotenv()
    access_id = os.environ["GCS_ACCESS_KEY_ID"]
    secret = os.environ["GCS_SECRET_ACCESS_KEY"]

    con.execute("INSTALL httpfs")
    con.execute("LOAD httpfs")
    con.execute("DROP SECRET IF EXISTS gcs_secret")

    con.execute(f"""
        CREATE SECRET gcs_secret (
            TYPE s3,
            KEY_ID '{access_id}',
            SECRET '{secret}',
            ENDPOINT 'storage.googleapis.com',
            REGION 'auto',
            SCOPE 'gs://'
        )
    """)
