# TickerFlow Constitution

> Principles and stable facts. Change rarely. If something here conflicts with
> a spec, the constitution wins — update the spec instead.

## Project identity

- **Name:** TickerFlow
- **Type:** Real-time stock tick data pipeline (learning + lead demo)
- **Demo date:** Friday — AWS must be live

### Definition of done (demo)

The demo is successful only when **both** are true: the local Docker pipeline
runs live end-to-end **and** the AWS-deployed version is queryable (S3 + Athena).
Partial credit is not the goal — do not declare victory if only one side works.

## Non-negotiable principles

### 1. Local-first, AWS for demo

Every service must run in Docker on a laptop before it is deployed to AWS.
Local is for fast iteration; AWS is the presentation target.

### 2. No silent data loss

Invalid records are quarantined with a reason. Valid records are persisted.
Nothing is dropped without a log entry.

### 3. Decoupled data source

The producer is the only place that knows ticks are synthetic. Downstream
code (Kafka consumer, lake writer, Airflow) only sees validated tick objects.

### 4. Configuration via environment

All endpoints and credentials come from environment variables or `.env` files.
Never hardcode `localhost`, bucket names, or broker URLs in application code.

### 5. Decisions are documented

Any choice between two real alternatives gets an ADR in `memory/decisions/`
before implementation proceeds.

### 6. Independently runnable components

Producer, consumer, and query scripts must each run on their own for debugging.

### 7. Safely restartable without manual cleanup

Components must survive crash and restart without human intervention to fix state.
The Kafka consumer resumes from the last committed offset (at-least-once delivery).
Airflow retries failed DAG tasks per its default retry policy. Lake writes use
unique filenames per batch so restarts do not overwrite prior data.

### 8. Test before done

Each spec folder has `test.md`. A phase is not complete until those tests pass
and acceptance criteria in `spec.md` are checked off.

## Stable data contract

### Tick fields

**Fixed symbol list:** AAPL, MSFT, GOOGL, TSLA, AMZN only — not arbitrary
tickers. A closed list keeps Kafka partitioning predictable, Pydantic validation
simple, and demo queries easy to reason about.

| Field | Type | Rule |
|-------|------|------|
| `symbol` | string | One of: AAPL, MSFT, GOOGL, TSLA, AMZN |
| `price` | float | Must be > 0 |
| `volume` | int | Must be > 0 |
| `timestamp` | ISO 8601 UTC | Required |
| `side` | string | `buy` or `sell` — used in spec 004 for buy vs sell volume splits |

### Example tick (JSON)

```json
{
  "symbol": "AAPL",
  "price": 182.34,
  "volume": 500,
  "timestamp": "2026-06-30T10:31:05Z",
  "side": "buy"
}
```

## Stable infrastructure names

| Resource | Value |
|----------|-------|
| Kafka topic | `stock-ticks` |
| Kafka partition key | `symbol` |
| Lake bucket | `stock-lake` |
| Raw path pattern | `raw/symbol={symbol}/date={YYYY-MM-DD}/` |
| Enriched path pattern | `enriched/symbol={symbol}/date={YYYY-MM-DD}/` |
| Quarantine path pattern | `quarantine/date={YYYY-MM-DD}/` |

## Tech stack (locked for this project)

| Layer | Local | AWS |
|-------|-------|-----|
| Stream | Kafka (Docker) | Kafka on EC2 (Docker) |
| Validation | Pydantic (Python) | Same |
| Storage | MinIO | S3 |
| Query | DuckDB | Athena + Glue |
| Orchestration | Airflow (Docker) | Airflow on EC2 (Docker) |
| IaC | — | Terraform |
| Monitoring | Docker logs | CloudWatch |

## Out of scope (entire project)

- Real-time trading or order execution
- User authentication or multi-tenancy
- Exactly-once semantics (at-least-once is acceptable for demo)
- Schema registry (Avro/Protobuf) — JSON + Pydantic is enough for v1

## Secrets

- Never commit `.env`, AWS keys, or API tokens.
- Use `.env.example` with placeholder values only.
