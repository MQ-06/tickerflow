# Tests: Streaming Ingest

> Maps to acceptance criteria in [spec.md](spec.md). Run after `tasks.md` is complete.

## Prerequisites

- Docker and Docker Compose installed
- Repo root as working directory
- No process bound to port `9092`

## Test matrix

| ID | Acceptance criterion | Type | Section |
|----|---------------------|------|---------|
| T1 | Kafka (KRaft) starts without errors | Manual | §1 |
| T2 | Producer logs each published tick | Manual | §2 |
| T3 | Console consumer shows JSON on `stock-ticks` | Manual | §3 |
| T4 | All 5 symbols within 30 seconds | Manual | §3 |
| T5 | Same-symbol publish order preserved | Manual | §4 |
| T6 | Producer restart needs no manual cleanup | Manual | §5 |

---

## §1 — Kafka starts (T1)

**What:** Broker is healthy before producer runs.

**How:**

```bash
docker compose up -d
docker compose ps          # kafka service: healthy
docker compose logs kafka  # no fatal errors
```

**Pass if:** Kafka container is `running` and healthcheck reports healthy (or
`kafka-topics --bootstrap-server localhost:9092 --list` succeeds).

---

## §2 — Producer publishes (T2)

**What:** Producer connects and emits ticks.

**How:**

```bash
pip install -r requirements.txt
python -m src.producer.main
```

**Pass if:** stdout shows one log line per tick with `symbol`, `price`, and
`timestamp`. No connection errors after Kafka is healthy.

---

## §3 — Messages on topic (T3, T4)

**What:** Ticks are durable on Kafka and all symbols appear.

**How:** With producer running, in a second terminal:

```bash
docker compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic stock-ticks \
  --from-beginning \
  --timeout-ms 35000
```

**Pass if:**

- Each line is valid JSON with `symbol`, `price`, `volume`, `timestamp`, `side`
- Within 30 seconds you see all five: `AAPL`, `MSFT`, `GOOGL`, `TSLA`, `AMZN`
- `price` > 0, `side` is `buy` or `sell`

---

## §4 — Per-symbol ordering (T5)

**What:** Partition key = `symbol` keeps order per ticker.

**How:** From consumer output, filter one symbol (e.g. AAPL) and check
timestamps are non-decreasing.

```bash
# Quick check: pipe consumer output through jq
docker compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic stock-ticks \
  --timeout-ms 15000 | jq -r 'select(.symbol=="AAPL") | .timestamp'
```

**Pass if:** AAPL timestamps never go backwards (allow equal if same second).

---

## §5 — Clean restart (T6)

**What:** Constitution restart principle — no manual Kafka cleanup.

**How:**

1. Run producer for ~10 ticks; note last logged symbol/timestamp
2. `Ctrl+C` producer
3. Restart: `python -m src.producer.main`
4. Consumer still shows new messages appended to topic

**Pass if:** Producer reconnects without deleting topics or resetting offsets;
new ticks appear immediately.

---

## Automated tests (optional, add in implementation)

| File | Covers |
|------|--------|
| `tests/unit/test_tick_generator.py` | Synthetic tick shape matches constitution |
| `tests/unit/test_config.py` | Env vars load with defaults |

Run: `pytest tests/unit -q`

---

## Sign-off

- [ ] T1–T6 passed
- [ ] Tick acceptance criteria in `spec.md` checked
- [ ] Update `masterplan.md` — spec 001 → ✅ Done
