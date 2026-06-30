# Spec: Streaming Ingest

**Status:** done  
**Depends on:** none (first build phase)

## Problem

Ticks are generated continuously. Something must accept them at high frequency
and hold them safely until the validator is ready — without the producer
knowing or caring about downstream speed.

## User story

As a data engineer, I want a producer that emits realistic ticks into Kafka so
that the rest of the pipeline can consume them independently and in order per
symbol.

## Scope

### In scope

- Docker Compose stack with Kafka in **KRaft mode** (no Zookeeper)
- Python producer: synthetic ticks for 5 constitution symbols
- Publish JSON to topic `stock-ticks`, partition key = `symbol`
- Configurable tick interval via env var
- Producer retries Kafka connection with backoff

### Out of scope

- Pydantic validation (spec 002)
- Real market API integration
- Schema registry / Avro
- Multiple producers or load testing

## Inputs / outputs

| Step | Input | Output |
|------|-------|--------|
| Generate | Symbol list + random walk state | Tick dict (see constitution) |
| Publish | Tick dict | JSON message on `stock-ticks` |
| Buffer | Kafka | Durable ordered log per partition |

## Acceptance criteria

- [x] `docker compose up` starts Kafka (KRaft) without errors
- [x] Producer runs and logs each published tick
- [x] `kafka-console-consumer` shows JSON ticks on `stock-ticks` for all 5 symbols within 30 seconds
- [x] Ticks for the same symbol maintain publish order
- [x] Stopping and restarting the producer resumes publishing without manual Kafka cleanup

## References

- [ADR-001](../../memory/decisions/ADR-001-synthetic-data.md) — synthetic data
- [ADR-002](../../memory/decisions/ADR-002-kafka.md) — why Kafka
- [Constitution](../../memory/constitution.md) — fixed symbol list, restart principle
