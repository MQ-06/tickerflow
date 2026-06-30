# ADR-002: Kafka as the message broker

**Date:** 2026-06-30  
**Status:** accepted

## Context

The producer emits ticks faster than the consumer can always write to object
storage. We need a buffer between them that survives restarts and preserves
order per symbol.

## Decision

Use **Apache Kafka** with topic `stock-ticks`, partitioned by `symbol`.

## Alternatives considered

| Option | Pros | Cons | Why rejected |
|--------|------|------|--------------|
| Direct DB writes | Simple | DB chokes on high-frequency tiny writes | Wrong tool for event streams |
| RabbitMQ | Easy setup, good task queues | Not built for replayable log streams | Messages consumed once; weak replay story |
| AWS Kinesis | Managed, AWS-native | Vendor lock-in, different API, less portable skills | Kafka skills transfer wider; local dev harder |
| Redis Streams | Lightweight | Retention and ops at scale less proven for this pattern | Fine for small projects; weaker demo narrative |
| **Kafka** | Replay, order per partition, industry standard | Heavier local setup (Docker mitigates) | **Chosen** |

## Consequences

- Docker Compose runs Kafka locally; EC2 + Docker on AWS for demo.
- Consumer uses consumer groups for offset tracking (at-least-once delivery).
- Partition key = `symbol` so AAPL ticks stay ordered relative to each other.
