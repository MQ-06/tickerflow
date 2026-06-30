# Tests: Validation & Lake Storage

> Maps to acceptance criteria in [spec.md](spec.md). Requires spec 001 running.

## Prerequisites

- Kafka + producer running (spec 001)
- MinIO in `docker compose up`
- Consumer implemented per `plan.md`

## Test matrix

| ID | Acceptance criterion | Type | Section |
|----|---------------------|------|---------|
| T1 | Consumer processes messages continuously | Manual | §1 |
| T2 | Bad tick → quarantine, not lake | Manual | §2 |
| T3 | Valid ticks → Parquet under partition path | Manual | §3 |
| T4 | Consumer restart resumes from offset | Manual | §4 |
| T5 | Quarantine path `quarantine/date={date}/` | Manual | §2 |
| T6 | Unique batch filenames on restart | Manual | §4 |
| T7 | Bucket `stock-lake` auto-created | Manual | §3 |

---

## §1 — Consumer runs (T1)

**What:** Consumer stays up and logs processed ticks.

**How:**

```bash
docker compose up -d
python -m src.producer.main &   # background
python -m src.consumer.main
```

**Pass if:** Consumer logs show validated ticks; no crash after 2+ minutes.

---

## §2 — Quarantine bad data (T2, T5)

**What:** Invalid messages never reach `raw/`.

**How:** Publish a bad message (one of):

```bash
# Option A: kafka-console-producer with invalid JSON
docker compose exec -T kafka kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic stock-ticks <<'EOF'
{"symbol":"AAPL","price":-1,"volume":100,"timestamp":"2026-06-30T12:00:00Z","side":"buy"}
EOF
```

**Verify in MinIO** (console at `http://localhost:9001` or `mc` CLI):

- Object exists under `quarantine/date=YYYY-MM-DD/`
- **No** new file under `raw/` for that bad tick
- Consumer log mentions validation failure / quarantine

**Pass if:** Quarantine file contains the bad record + reason; lake unchanged for that event.

---

## §3 — Valid Parquet in lake (T3, T7)

**What:** Good ticks land as Parquet with hive partitions.

**How:** After 2+ minutes of producer + consumer:

```bash
# MinIO client example (if mc configured)
mc ls local/stock-lake/raw/ --recursive
```

Or open MinIO UI → bucket `stock-lake` → browse `raw/symbol=AAPL/date=.../`.

**Pass if:**

- `.parquet` files exist under `raw/symbol={SYMBOL}/date={YYYY-MM-DD}/`
- Files are non-empty
- Reading one file (pyarrow or DuckDB) shows expected columns

```python
import pyarrow.parquet as pq
pq.read_table("path/to/file.parquet").to_pandas().head()
```

---

## §4 — Offset resume & unique files (T4, T6)

**What:** Restart does not reprocess committed messages or overwrite Parquet.

**How:**

1. Note consumer log offset or message count after 1 minute
2. `Ctrl+C` consumer; wait for producer to emit ~20 more ticks
3. Restart consumer
4. List Parquet filenames before and after restart

**Pass if:**

- Consumer does not re-log the same tick IDs/timestamps from before shutdown
- New Parquet files have **new** names (e.g. UUID/timestamp in filename), not overwrites

---

## Automated tests (optional)

| File | Covers |
|------|--------|
| `tests/unit/test_tick_model.py` | Pydantic rejects negative price, unknown symbol |
| `tests/unit/test_tick_model.py` | Valid constitution tick passes |
| `tests/integration/test_writer.py` | Parquet round-trip (mock S3/MinIO) |

Run: `pytest tests/unit -q`

---

## Sign-off

- [ ] T1–T7 passed
- [ ] Acceptance criteria in `spec.md` checked
- [ ] Update `masterplan.md` — spec 002 → ✅ Done
