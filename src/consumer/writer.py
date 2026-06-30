import json
import logging
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from io import BytesIO

import boto3
import pyarrow as pa
import pyarrow.parquet as pq
from botocore.exceptions import ClientError

from src.common.config import ConsumerConfig
from src.common.models.tick import Tick

logger = logging.getLogger(__name__)


class LakeWriter:
    def __init__(self, config: ConsumerConfig) -> None:
        self._config = config
        self._client = boto3.client(
            "s3",
            endpoint_url=config.s3_endpoint,
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
            region_name="us-east-1",
        )
        self._ensure_bucket()

    def _ensure_bucket(self, max_retries: int = 30, delay_sec: float = 2.0) -> None:
        bucket = self._config.s3_bucket
        for attempt in range(1, max_retries + 1):
            try:
                self._client.head_bucket(Bucket=bucket)
                logger.info("Bucket %s exists", bucket)
                return
            except ClientError as exc:
                code = exc.response.get("Error", {}).get("Code", "")
                if code not in ("404", "NoSuchBucket", "403"):
                    raise
                try:
                    self._client.create_bucket(Bucket=bucket)
                    logger.info("Created bucket %s", bucket)
                    return
                except ClientError as create_exc:
                    if create_exc.response.get("Error", {}).get("Code") == "BucketAlreadyOwnedByYou":
                        return
                    if attempt == max_retries:
                        raise
                    wait = min(delay_sec * attempt, 10)
                    logger.warning(
                        "MinIO not ready (attempt %s/%s), retrying in %.1fs...",
                        attempt,
                        max_retries,
                        wait,
                    )
                    time.sleep(wait)

    def write_parquet_batch(self, ticks: list[Tick]) -> list[str]:
        if not ticks:
            return []

        groups: dict[tuple[str, str], list[Tick]] = defaultdict(list)
        for tick in ticks:
            groups[(tick.symbol, tick.partition_date())].append(tick)

        written_keys: list[str] = []
        for (symbol, date), group_ticks in groups.items():
            rows = [t.to_parquet_row() for t in group_ticks]
            table = pa.Table.from_pylist(rows)
            buffer = BytesIO()
            pq.write_table(table, buffer)
            buffer.seek(0)

            key = (
                f"raw/symbol={symbol}/date={date}/"
                f"ticks_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}_{uuid.uuid4().hex[:8]}.parquet"
            )
            self._client.put_object(
                Bucket=self._config.s3_bucket,
                Key=key,
                Body=buffer.getvalue(),
                ContentType="application/octet-stream",
            )
            written_keys.append(key)
            logger.info("Wrote %s ticks to s3://%s/%s", len(group_ticks), self._config.s3_bucket, key)

        return written_keys

    def write_quarantine(self, raw_message: dict, errors: list[str]) -> str:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        payload = {
            "raw": raw_message,
            "errors": errors,
            "quarantined_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        body = json.dumps(payload) + "\n"
        key = f"quarantine/date={date}/rejected_{uuid.uuid4().hex}.jsonl"
        self._client.put_object(
            Bucket=self._config.s3_bucket,
            Key=key,
            Body=body.encode("utf-8"),
            ContentType="application/json",
        )
        logger.warning("Quarantined message at s3://%s/%s: %s", self._config.s3_bucket, key, errors)
        return key

    def list_keys(self, prefix: str) -> list[str]:
        keys: list[str] = []
        paginator = self._client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self._config.s3_bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                keys.append(obj["Key"])
        return keys
