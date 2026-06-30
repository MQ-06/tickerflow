# Spec: Validation & Lake Storage

**Status:** draft  
**Depends on:** 001-streaming-ingest

## Problem

Raw ticks arriving on Kafka are not guaranteed valid — a malformed price,
missing field, or unknown symbol must not corrupt downstream storage or crash
the pipeline. Valid data needs a durable, queryable home.

## User story

As a data engineer, I want every tick checked against a strict schema before
it's stored, so that bad data is quarantined with a reason instead of
silently polluting the data lake.

## Scope

### In scope

- Kafka consumer reading from `stock-ticks` (same `kafka-python` client as producer)
- Pydantic model validating each tick against the constitution's data contract
- Valid ticks written as Parquet to MinIO, partitioned by `symbol` / `date`
- Invalid ticks written to quarantine path with reason — not dropped
- Batch writes (every N ticks or M seconds) to avoid tiny Parquet files
- Consumer runs independently and resumes from last committed offset on restart

### Out of scope

- Query layer (spec 003)
- Real S3 (local MinIO only; spec 005 swaps endpoint via env)
- Deduplication / exactly-once semantics (constitution: at-least-once is acceptable)

## Inputs / outputs

| Step | Input | Output |
|------|-------|--------|
| Consume | Kafka message (JSON) | Parsed dict |
| Validate | Dict | Valid `Tick` object or `ValidationError` |
| Route valid | `Tick` batch | Parquet under `raw/symbol={symbol}/date={date}/` |
| Route invalid | Failed message + reason | JSONL under `quarantine/date={date}/` |

## Acceptance criteria

- [ ] Consumer connects to Kafka and processes messages continuously
- [ ] A deliberately malformed message (e.g. negative price) lands in quarantine with a logged reason, not in the lake
- [ ] Valid ticks appear as `.parquet` files under `raw/symbol={symbol}/date={date}/` in MinIO
- [ ] Restarting the consumer does not reprocess already-committed messages (constitution: restartable without manual cleanup)
- [ ] Quarantine path follows `quarantine/date={date}/`
- [ ] Lake writes use unique filenames per batch so restarts do not overwrite prior data

## Risks

| Risk | Mitigation |
|------|------------|
| One Parquet file per tick hurts query performance | Batch flush every N ticks or M seconds |
| MinIO not reachable on consumer start | Retry with backoff (same pattern as producer → Kafka) |

## References

- [ADR-003](../../memory/decisions/ADR-003-minio-then-s3.md) — MinIO then S3
- [Constitution](../../memory/constitution.md) — data contract, no-silent-loss, restart principle
