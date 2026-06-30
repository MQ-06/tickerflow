import tempfile
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from src.query.lake_connection import connect_lake, load_lake_query_config, tick_count


def _write_sample_parquet(directory: Path) -> None:
    aapl = [
        {
            "symbol": "AAPL",
            "price": 180.0,
            "volume": 100,
            "timestamp": "2026-06-30T10:00:00Z",
            "side": "buy",
        }
    ]
    msft = [
        {
            "symbol": "MSFT",
            "price": 420.0,
            "volume": 200,
            "timestamp": "2026-06-30T10:00:01Z",
            "side": "sell",
        }
    ]
    pq.write_table(pa.Table.from_pylist(aapl), directory / "aapl.parquet")
    pq.write_table(pa.Table.from_pylist(msft), directory / "msft.parquet")


def test_query_local_parquet_glob():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_sample_parquet(root)
        glob = str(root / "**" / "*.parquet")
        config = load_lake_query_config(parquet_glob=glob)
        con = connect_lake(config)
        assert tick_count(con) == 2

        avg = con.execute(
            "SELECT symbol, AVG(price) AS avg_price FROM ticks GROUP BY symbol ORDER BY symbol"
        ).fetchall()
        assert len(avg) == 2
        assert avg[0][0] == "AAPL"
