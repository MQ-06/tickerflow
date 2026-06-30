import os
from dataclasses import dataclass
from urllib.parse import urlparse

import duckdb

from src.common.config import load_consumer_config


@dataclass(frozen=True)
class LakeQueryConfig:
    s3_endpoint: str
    s3_host: str
    s3_use_ssl: bool
    s3_bucket: str
    aws_access_key_id: str
    aws_secret_access_key: str
    raw_glob: str


def load_lake_query_config(parquet_glob: str | None = None) -> LakeQueryConfig:
    consumer = load_consumer_config()
    endpoint = os.getenv("S3_ENDPOINT", consumer.s3_endpoint)
    bucket = os.getenv("S3_BUCKET", consumer.s3_bucket)

    if parquet_glob:
        raw_glob = parquet_glob
        s3_host = ""
        s3_use_ssl = False
    else:
        parsed = urlparse(endpoint)
        s3_host = parsed.netloc or parsed.path
        s3_use_ssl = parsed.scheme == "https"
        raw_glob = f"s3://{bucket}/raw/**/*.parquet"

    return LakeQueryConfig(
        s3_endpoint=endpoint,
        s3_host=s3_host,
        s3_use_ssl=s3_use_ssl,
        s3_bucket=bucket,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", consumer.aws_access_key_id),
        aws_secret_access_key=os.getenv(
            "AWS_SECRET_ACCESS_KEY", consumer.aws_secret_access_key
        ),
        raw_glob=raw_glob,
    )


def connect_lake(config: LakeQueryConfig) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(database=":memory:")
    con.execute("INSTALL httpfs; LOAD httpfs;")

    if config.raw_glob.startswith("s3://"):
        con.execute(f"SET s3_endpoint='{config.s3_host}';")
        con.execute(f"SET s3_use_ssl={'true' if config.s3_use_ssl else 'false'};")
        con.execute("SET s3_url_style='path';")
        con.execute(f"SET s3_access_key_id='{config.aws_access_key_id}';")
        con.execute(f"SET s3_secret_access_key='{config.aws_secret_access_key}';")

    con.execute(
        f"CREATE OR REPLACE VIEW ticks AS SELECT * FROM read_parquet('{config.raw_glob}');"
    )
    return con


def tick_count(con: duckdb.DuckDBPyConnection) -> int:
    return int(con.execute("SELECT COUNT(*) FROM ticks").fetchone()[0])
