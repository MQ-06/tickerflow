# Spec: Batch Enrichment (Airflow)

**Status:** draft  
**Depends on:** 002-validation-lake, 003-query-layer

## Problem

Some metrics (moving averages, daily OHLC, buy vs sell volume splits) cannot be
computed from a single tick — they need a window of accumulated history. Doing
this on every tick would be wasteful; it belongs on a schedule.

## User story

As a data engineer, I want a scheduled job that reads accumulated raw ticks and
computes derived metrics, so analysis is available without recomputing on every
single event.

## Scope

### In scope

- One Airflow DAG on a configurable schedule (default: every 15 minutes)
- Read raw Parquet lake since last successful DAG run
- Compute per symbol: 5-minute moving average, OHLC (open/high/low/close), total volume
- Compute per symbol: **buy volume vs sell volume** (uses constitution `side` field)
- Write enriched dataset to `enriched/symbol={symbol}/date={date}/`
- DAG visible and runnable in Airflow UI (demo requirement)
- Failed tasks retry per Airflow defaults; prior enriched data not corrupted

### Out of scope

- Backfilling historical runs beyond one manual test
- Complex windowing beyond moving average, OHLC, and buy/sell splits
- Alerting on enrichment failure (CloudWatch in spec 005, AWS-side)

## Inputs / outputs

| Step | Input | Output |
|------|-------|--------|
| Read | Raw Parquet since last run | In-memory table (pandas/pyarrow) |
| Compute | Raw ticks | Moving avg, OHLC, buy/sell volume per symbol |
| Write | Enriched rows | Parquet under `enriched/symbol={symbol}/date={date}/` |

## Acceptance criteria

- [ ] DAG appears in Airflow UI and runs successfully on schedule (or manual trigger)
- [ ] Enriched Parquet contains `open`, `high`, `low`, `close`, `volume`, `buy_volume`, `sell_volume`, and `moving_avg` columns
- [ ] OHLC values match a manual calculation on a small known sample
- [ ] Buy/sell volume splits sum to total volume for each symbol-window
- [ ] Simulated failure (e.g. MinIO unavailable mid-run) does not corrupt prior enriched files; Airflow shows failure clearly and retries

## Risks

| Risk | Mitigation |
|------|------------|
| Airflow setup eats build time | Base on official Airflow docker-compose quickstart; do not build from scratch |
| OHLC wrong across partition boundaries | Test one symbol with a small known dataset first |

## References

- [Constitution](../../memory/constitution.md) — `side` field, enriched path, Airflow retry principle
