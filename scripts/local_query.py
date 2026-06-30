#!/usr/bin/env python3
"""Run demo SQL queries against the Parquet data lake via DuckDB."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.query.lake_connection import connect_lake, load_lake_query_config, tick_count

DEFAULT_QUERIES = (
    REPO_ROOT / "queries" / "avg_price_by_symbol.sql",
    REPO_ROOT / "queries" / "latest_ticks.sql",
    REPO_ROOT / "queries" / "tick_count_by_symbol.sql",
)


def _read_sql(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _print_result(title: str, sql: str, con) -> None:
    print(f"\n=== {title} ===")
    result = con.execute(sql)
    rows = result.fetchall()
    columns = [col[0] for col in result.description]
    if not rows:
        print("(no rows)")
        return

    widths = [len(str(col)) for col in columns]
    for row in rows:
        for idx, value in enumerate(row):
            widths[idx] = max(widths[idx], len(str(value)))

    header = " | ".join(str(col).ljust(widths[i]) for i, col in enumerate(columns))
    print(header)
    print("-+-".join("-" * w for w in widths))
    for row in rows:
        print(" | ".join(str(value).ljust(widths[i]) for i, value in enumerate(row)))


def run_queries(query_paths: list[Path], parquet_glob: str | None) -> int:
    config = load_lake_query_config(parquet_glob=parquet_glob)

    try:
        con = connect_lake(config)
        count = tick_count(con)
    except Exception:
        print(f"No data found in lake ({config.raw_glob}).")
        print("Start producer + consumer and wait for Parquet files under raw/.")
        return 1

    if count == 0:
        print(f"No data found in lake ({config.raw_glob}).")
        print("Start producer + consumer and wait for Parquet files under raw/.")
        return 1

    print(f"Lake: {config.raw_glob} ({count} ticks)")

    for path in query_paths:
        sql = _read_sql(path)
        _print_result(path.name, sql, con)

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Query TickerFlow lake with DuckDB")
    parser.add_argument(
        "--query",
        type=Path,
        action="append",
        help="SQL file to run (default: all demo queries)",
    )
    parser.add_argument(
        "--parquet-glob",
        help="Override lake path (local glob for tests), e.g. /tmp/empty/**/*.parquet",
    )
    args = parser.parse_args()

    query_paths = args.query or list(DEFAULT_QUERIES)
    for path in query_paths:
        if not path.exists():
            print(f"Query file not found: {path}")
            return 1

    return run_queries(query_paths, args.parquet_glob)


if __name__ == "__main__":
    sys.exit(main())
