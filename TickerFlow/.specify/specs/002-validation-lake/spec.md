# Spec: Validation & Data Lake

**Status:** draft  
**Depends on:** 001-streaming-ingest

## Problem

Not every message on Kafka is trustworthy. Bad ticks (negative price, unknown
symbol) must be caught before they reach analytics storage. Valid ticks must
land in the lake in a format and layout that makes SQL queries fast and cheap.

## User story

As a data engineer, I want a consumer that validates each tick and writes valid
rows as Parquet in partitioned folders, with invalid rows quarantined, so
analysts only query clean data.

## Scope

### In scope

- Pydantic `Tick` model matching constitution
- Kafka consumer reading `stock-ticks`
- Valid → Parquet batches to `raw/symbol=…/date=…/`
- Invalid → JSON lines to `quarantine/date=…/`
- MinIO in Docker Compose
- boto3 writer with env-based endpoint

### Out of scope

- Exactly-once semantics
- Real-time SQL queries (spec 003)
- Enrichment (spec 004)

## Inputs / outputs

| Step | Input | Output |
|------|-------|--------|
| Consume | Kafka JSON message | Raw dict |
| Validate | Raw dict | `Tick` model or validation error |
| Write valid | Batch of `Tick` | `.parquet` file in lake |
| Write invalid | Failed message + reason | `.jsonl` in quarantine |

## Acceptance criteria

- [ ] Tick with `price: -1` lands in quarantine, not `raw/`
- [ ] Valid ticks appear as Parquet under correct partition paths
- [ ] Consumer survives restart and continues from last offset
- [ ] MinIO bucket `stock-lake` created on first run

## References

- [ADR-003](../../memory/decisions/ADR-003-minio-then-s3.md)
