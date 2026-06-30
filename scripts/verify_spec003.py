#!/usr/bin/env python3
"""End-to-end verification for spec 003 (query layer)."""

import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pyarrow as pa
import pyarrow.parquet as pq

from src.common.config import DEFAULT_SYMBOLS
from src.producer.tick_generator import SEED_PRICES
from src.query.lake_connection import connect_lake, load_lake_query_config, tick_count


def run_local_query(extra_args: list[str] | None = None) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(REPO_ROOT / "scripts" / "local_query.py")]
    if extra_args:
        cmd.extend(extra_args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=120)


def main() -> int:
    print("T5: query files exist...")
    for name in (
        "avg_price_by_symbol.sql",
        "latest_ticks.sql",
        "tick_count_by_symbol.sql",
    ):
        path = REPO_ROOT / "queries" / name
        if not path.exists():
            print(f"  FAIL: missing {path}")
            return 1
    print("  OK")

    print("T1: local_query.py runs all demo queries...")
    result = run_local_query()
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        print("  FAIL: script returned non-zero")
        return 1
    if "avg_price_by_symbol.sql" not in result.stdout:
        print("  FAIL: expected query output missing")
        return 1
    print("  OK")

    print("T2/T3/T4: validating query results via DuckDB...")
    config = load_lake_query_config()
    con = connect_lake(config)
    count = tick_count(con)
    if count <= 0:
        print("  FAIL: no ticks in lake")
        return 1

    latest_sql = (REPO_ROOT / "queries" / "latest_ticks.sql").read_text()
    latest_rows = con.execute(latest_sql).fetchall()
    if len(latest_rows) != 5:
        print(f"  FAIL: expected 5 latest rows, got {len(latest_rows)}")
        return 1

    symbols = {row[0] for row in latest_rows}
    if symbols != set(DEFAULT_SYMBOLS):
        print(f"  FAIL: unexpected symbols {symbols}")
        return 1
    print("  OK: latest tick per symbol (5 rows)")

    avg_sql = (REPO_ROOT / "queries" / "avg_price_by_symbol.sql").read_text()
    avg_rows = {row[0]: float(row[1]) for row in con.execute(avg_sql).fetchall()}
    for symbol in DEFAULT_SYMBOLS:
        avg = avg_rows.get(symbol)
        seed = SEED_PRICES[symbol]
        if avg is None or avg <= 0:
            print(f"  FAIL: bad avg for {symbol}: {avg}")
            return 1
        low, high = seed * 0.5, seed * 1.5
        if not (low <= avg <= high):
            print(f"  FAIL: avg {avg} for {symbol} outside [{low}, {high}]")
            return 1
    print("  OK: average prices plausible")

    count_sql = (REPO_ROOT / "queries" / "tick_count_by_symbol.sql").read_text()
    total = sum(row[1] for row in con.execute(count_sql).fetchall())
    if total <= 0:
        print("  FAIL: tick count is zero")
        return 1
    print(f"  OK: total tick count = {total}")

    print("T6: empty lake handled gracefully...")
    with tempfile.TemporaryDirectory() as tmp:
        empty_glob = str(Path(tmp) / "**" / "*.parquet")
        empty_result = run_local_query(["--parquet-glob", empty_glob])
        if empty_result.returncode == 0:
            print("  FAIL: expected non-zero exit for empty lake")
            return 1
        if "No data found" not in empty_result.stdout:
            print("  FAIL: missing friendly empty-lake message")
            print(empty_result.stdout)
            return 1
    print("  OK")

    print("All automated spec-003 checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
