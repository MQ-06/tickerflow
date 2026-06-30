# TickerFlow — Master Plan

> **Agent entry point.** Read this file first. It tracks project status and links
> to every spec and decision. Do not code without reading the relevant
> `spec.md` → `plan.md` → `tasks.md` for the current phase.

## What this project is

TickerFlow is a real-time stock market data pipeline. It ingests a continuous
stream of simulated stock ticks, validates each one, stores valid data in a
queryable data lake, computes periodic enrichments (OHLC, moving averages), and
is provisioned as code. Built **local-first in Docker**, deployed to **AWS**
for the Friday demo.

**Problem it solves:** data that arrives continuously and fast must not be lost,
bad data must not corrupt analysis, storage must stay cheap at scale, and the
whole system must be reproducible and observable.

## Architecture at a glance

```text
Producer → Kafka → Consumer (Pydantic) → Parquet lake (MinIO/S3)
                                              ↓
                         Airflow (scheduled) → enriched Parquet
                                              ↓
                              DuckDB local / Athena on AWS
```

Two speeds, one system:

- **Streaming path** — ingest, validate, store (runs continuously).
- **Batch path** — enrichment on a schedule (Airflow).

Terraform provisions AWS. CloudWatch monitors it. Neither sits in the data flow.

## Constitution (summary)

Full detail: [memory/constitution.md](memory/constitution.md)

- Local-first, AWS for demo — every component runs in Docker before AWS.
- No silent data loss — invalid ticks go to quarantine, never dropped quietly.
- Swappable data source — synthetic now, real API later without downstream changes.
- Env-based config — no hardcoded endpoints; switch local ↔ AWS via env vars.
- Every major choice has an ADR — no unexplained tool picks.

## Phase / spec status

| # | Spec folder | Goal | Status |
|---|-------------|------|--------|
| 001 | [streaming-ingest](specs/001-streaming-ingest/) | Producer publishes ticks to Kafka | 🟨 Spec written |
| 002 | [validation-lake](specs/002-validation-lake/) | Validate with Pydantic, write Parquet to lake | 🟨 Spec written |
| 003 | [query-layer](specs/003-query-layer/) | SQL queries via DuckDB / Athena | 🟨 Spec written |
| 004 | [batch-enrichment](specs/004-batch-enrichment/) | Airflow DAG for OHLC / moving averages | 🟨 Spec written |
| 005 | [aws-deployment](specs/005-aws-deployment/) | Terraform + live AWS pipeline | 🟨 Spec written |
| 006 | [demo-presentation](specs/006-demo-presentation/) | Friday demo script and fallbacks | 🟨 Spec written |

**Status key:** ⬜ Not started · 🟨 Spec written · 🟦 Planned · 🟧 In progress · ✅ Done

**Current focus:** Phase 001 — streaming ingest

## Decisions log (ADRs)

| ADR | Decision | One-line why |
|-----|----------|--------------|
| [001](memory/decisions/ADR-001-synthetic-data.md) | Synthetic ticks, not live API | Reliable demo — no rate limits or network failures |
| [002](memory/decisions/ADR-002-kafka.md) | Kafka, not RabbitMQ or Kinesis | Replayable ordered stream at high throughput |
| [003](memory/decisions/ADR-003-minio-then-s3.md) | MinIO locally, S3 on AWS | Same S3 API — zero code change at deploy |
| [004](memory/decisions/ADR-004-aws-kafka-airflow.md) | EC2 + Docker (not MSK/MWAA) | Fast, cheap enough for a 3-day demo |

Full detail: [memory/decisions/](memory/decisions/)

## Demo target (Friday)

Live AWS pipeline: producer → Kafka → validation → S3 → Athena query → Airflow
enrichment → CloudWatch logs. Plus clear **why** for each architectural choice.
Full script: [specs/006-demo-presentation/](specs/006-demo-presentation/)

## How to work in this repo

1. Check the status table above.
2. Open `specs/NNN-name/spec.md` — what and why (no implementation detail).
3. Read `plan.md` — how. Then `tasks.md` — do checklist.
4. Implement task by task; update status here when a phase completes.
5. Hit a tradeoff mid-build? Write an ADR first, then continue.
