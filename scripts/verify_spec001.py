#!/usr/bin/env python3
"""End-to-end verification for spec 001 (streaming ingest)."""

import json
import subprocess
import sys
import time
from datetime import datetime

from kafka import KafkaConsumer

REQUIRED_SYMBOLS = {"AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"}
BOOTSTRAP = "localhost:9092"
TOPIC = "stock-ticks"
TIMEOUT_SEC = 35


def run(cmd: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def check_docker_kafka() -> None:
    result = run(["docker", "compose", "ps", "--format", "json"])
    if result.returncode != 0:
        raise SystemExit(f"docker compose ps failed: {result.stderr}")
    if "kafka" not in result.stdout.lower():
        raise SystemExit("Kafka service not found in docker compose ps output")


def consume_ticks(timeout_sec: int) -> list[dict]:
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=[BOOTSTRAP],
        auto_offset_reset="earliest",
        consumer_timeout_ms=timeout_sec * 1000,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )
    ticks = []
    for message in consumer:
        ticks.append(message.value)
    consumer.close()
    return ticks


def main() -> int:
    print("T1: checking docker kafka...")
    check_docker_kafka()
    print("  OK")

    print("T3/T4: consuming ticks from topic...")
    ticks = consume_ticks(TIMEOUT_SEC)
    if not ticks:
        print("  FAIL: no messages received")
        return 1

    symbols = {t["symbol"] for t in ticks}
    missing = REQUIRED_SYMBOLS - symbols
    if missing:
        print(f"  FAIL: missing symbols: {missing}")
        return 1

    for tick in ticks:
        if tick["price"] <= 0 or tick["volume"] <= 0:
            print(f"  FAIL: invalid tick: {tick}")
            return 1
        if tick["side"] not in ("buy", "sell"):
            print(f"  FAIL: bad side: {tick}")
            return 1

    print(f"  OK: {len(ticks)} messages, all 5 symbols present")

    print("T5: checking AAPL timestamp ordering...")
    aapl_times = [
        datetime.fromisoformat(t["timestamp"].replace("Z", "+00:00"))
        for t in ticks
        if t["symbol"] == "AAPL"
    ]
    if len(aapl_times) >= 2:
        for prev, curr in zip(aapl_times, aapl_times[1:]):
            if curr < prev:
                print("  FAIL: AAPL timestamps went backwards")
                return 1
    print("  OK")

    print("All automated spec-001 checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
