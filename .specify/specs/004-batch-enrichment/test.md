# Tests: Batch Enrichment (Airflow)

> Maps to acceptance criteria in [spec.md](spec.md). Requires raw Parquet in lake.

## Prerequisites

- Specs 001–002 running; ≥ 15 minutes of raw data (or manual DAG trigger after shorter run)
- Airflow UI at `http://localhost:8080`
- DAG `stock_enrichment` deployed to `dags/`

## Test matrix

| ID | Acceptance criterion | Type | Section |
|----|---------------------|------|---------|
| T1 | Airflow UI accessible | Manual | §1 |
| T2 | DAG run succeeds (green) | Manual | §2 |
| T3 | Enriched Parquet schema correct | Manual | §3 |
| T4 | OHLC matches manual sample | Manual | §4 |
| T5 | Buy/sell volumes sum to total | Manual | §5 |
| T6 | Failure does not corrupt prior enriched data | Manual | §6 |
| T7 | DuckDB can query enriched data | Manual | §7 |

---

## §1 — Airflow UI (T1)

**What:** Scheduler and webserver are up.

**How:**

```bash
docker compose up -d   # includes Airflow services
open http://localhost:8080   # default user/pass per compose file
```

**Pass if:** UI loads; DAG `stock_enrichment` visible in list.

---

## §2 — Successful DAG run (T2)

**What:** DAG completes without error.

**How:**

1. Airflow UI → `stock_enrichment` → **Trigger DAG**
2. Open latest run → all tasks green

Or wait for scheduled run (15 min).

**Pass if:** Run state = `success`; no task in `failed` (after retries exhausted).

---

## §3 — Enriched files exist (T3)

**What:** Output lands in correct path with expected columns.

**How:** Browse MinIO `enriched/symbol=AAPL/date=.../` or:

```bash
mc ls local/stock-lake/enriched/ --recursive
```

Read schema:

```python
import pyarrow.parquet as pq
pq.read_schema("path/to/enriched.parquet")
```

**Pass if:** Columns include at minimum:
`open`, `high`, `low`, `close`, `volume`, `buy_volume`, `sell_volume`, `moving_avg`
(plus `symbol`, window timestamps per plan).

---

## §4 — OHLC correctness (T4)

**What:** Aggregations match hand calculation.

**How:**

1. Export a small raw sample for one symbol (10–20 ticks) to CSV
2. Compute OHLC by hand in a spreadsheet
3. Compare to enriched row for same window

**Pass if:** `open` = first price, `close` = last, `high` = max, `low` = min in window.

---

## §5 — Buy/sell split (T5)

**What:** `side` field used correctly.

**How:** On enriched row for a window:

```text
buy_volume + sell_volume == volume
```

**Pass if:** Equality holds for each symbol-window row tested.

---

## §6 — Failure handling (T6)

**What:** Airflow shows failure; prior enriched files intact.

**How:**

1. Note existing enriched files and checksums/sizes
2. Stop MinIO: `docker compose stop minio`
3. Trigger DAG → expect task failure
4. Restart MinIO; note Airflow retry behavior
5. Compare enriched files from step 1

**Pass if:** Failed run visible in UI; **no truncation/overwrite** of pre-existing enriched Parquet.

---

## §7 — Query enriched via DuckDB (T7)

**What:** Spec 003 tooling works on enriched layer.

**How:**

```sql
-- via scripts/local_query.py or DuckDB CLI
SELECT symbol, open, high, low, close, moving_avg
FROM read_parquet('enriched/**/*.parquet')
LIMIT 5;
```

**Pass if:** Returns rows with sensible numeric values.

---

## Sign-off

- [ ] T1–T7 passed
- [ ] Acceptance criteria in `spec.md` checked
- [ ] Update `masterplan.md` — spec 004 → ✅ Done
