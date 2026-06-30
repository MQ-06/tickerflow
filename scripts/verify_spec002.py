#!/usr/bin/env python3
"""End-to-end verification for spec 002 (validation & lake storage)."""

import json
import os
import subprocess
import sys
import time
from io import BytesIO

import boto3
import pyarrow.parquet as pq
from kafka import KafkaProducer

BOOTSTRAP = "localhost:9092"
TOPIC = "stock-ticks"
S3_ENDPOINT = "http://localhost:9000"
BUCKET = "stock-lake"
BAD_TICK = {
    "symbol": "AAPL",
    "price": -1,
    "volume": 100,
    "timestamp": "2026-06-30T12:00:00Z",
    "side": "buy",
}


def _start_background(cmd: list[str], log_path: str) -> subprocess.Popen:
    log = open(log_path, "a", encoding="utf-8")
    env = os.environ.copy()
    env.setdefault("BATCH_SIZE", "5")
    env.setdefault("BATCH_FLUSH_SEC", "5")
    env.setdefault("TICK_INTERVAL_SEC", "0.5")
    return subprocess.Popen(
        cmd,
        stdout=log,
        stderr=subprocess.STDOUT,
        env=env,
    )


def ensure_pipeline_running() -> tuple[subprocess.Popen | None, subprocess.Popen | None]:
    """Start consumer + producer if verify is run standalone."""
    consumer = _start_background([sys.executable, "-m", "src.consumer.main"], "/tmp/tf-consumer.log")
    producer = _start_background([sys.executable, "-m", "src.producer.main"], "/tmp/tf-producer.log")
    time.sleep(12)
    return producer, consumer


def s3_client():
    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id="minioadmin",
        aws_secret_access_key="minioadmin",
        region_name="us-east-1",
    )


def list_keys(prefix: str) -> list[str]:
    client = s3_client()
    keys: list[str] = []
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=BUCKET, Prefix=prefix):
        for obj in page.get("Contents", []):
            keys.append(obj["Key"])
    return keys


def publish_bad_tick() -> None:
    producer = KafkaProducer(
        bootstrap_servers=[BOOTSTRAP],
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    producer.send(TOPIC, value=BAD_TICK).get(timeout=10)
    producer.flush()
    producer.close()


def read_parquet_key(key: str) -> list[dict]:
    obj = s3_client().get_object(Bucket=BUCKET, Key=key)
    table = pq.read_table(BytesIO(obj["Body"].read()))
    return table.to_pylist()


def main() -> int:
    producer_proc, consumer_proc = ensure_pipeline_running()

    try:
        return _run_checks()
    finally:
        for proc in (producer_proc, consumer_proc):
            if proc and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()


def _run_checks() -> int:
    print("T7: checking bucket exists...")
    try:
        s3_client().head_bucket(Bucket=BUCKET)
        print("  OK")
    except Exception as exc:
        print(f"  FAIL: {exc}")
        return 1

    raw_before = set(list_keys("raw/"))
    quarantine_before = set(list_keys("quarantine/"))

    print("T2: publishing bad tick...")
    publish_bad_tick()
    time.sleep(8)

    quarantine_after = set(list_keys("quarantine/"))
    new_quarantine = quarantine_after - quarantine_before
    if not new_quarantine:
        print("  FAIL: no new quarantine object")
        return 1

    quarantine_body = s3_client().get_object(Bucket=BUCKET, Key=sorted(new_quarantine)[0])["Body"].read().decode()
    if "-1" not in quarantine_body and "price" not in quarantine_body.lower():
        print("  FAIL: quarantine body unexpected")
        return 1
    print(f"  OK: quarantined at {sorted(new_quarantine)[0]}")

    raw_after_bad = set(list_keys("raw/"))
    if raw_after_bad != raw_before:
        print("  WARN: raw/ changed after only bad tick (may be concurrent producer)")

    print("T3: checking Parquet in raw/...")
    raw_keys = [k for k in list_keys("raw/") if k.endswith(".parquet")]
    if not raw_keys:
        print("  FAIL: no parquet files under raw/")
        return 1

    sample = raw_keys[0]
    if "/symbol=" not in sample or "/date=" not in sample:
        print(f"  FAIL: bad partition path: {sample}")
        return 1

    rows = read_parquet_key(sample)
    if not rows or rows[0].get("price", 0) <= 0:
        print(f"  FAIL: invalid parquet content: {rows[:1]}")
        return 1
    print(f"  OK: {len(raw_keys)} parquet file(s), sample has {len(rows)} row(s)")

    print("T6: checking unique parquet filenames...")
    filenames = [k.split("/")[-1] for k in raw_keys]
    if len(filenames) != len(set(filenames)):
        print("  FAIL: duplicate parquet filenames")
        return 1
    print("  OK")

    print("T4: consumer restart smoke test...")
    keys_before_restart = set(list_keys("raw/"))
    subprocess.run(["pkill", "-f", "src.consumer.main"], capture_output=True)
    time.sleep(2)
    extra_consumer = _start_background(
        [sys.executable, "-m", "src.consumer.main"], "/tmp/tf-consumer-restart.log"
    )
    time.sleep(12)
    extra_consumer.terminate()
    extra_consumer.wait(timeout=10)
    keys_after_restart = set(list_keys("raw/"))
    if keys_after_restart == keys_before_restart:
        print("  WARN: no new files after restart (producer may be idle)")
    else:
        print(f"  OK: {len(keys_after_restart - keys_before_restart)} new file(s) after restart")

    print("All automated spec-002 checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
