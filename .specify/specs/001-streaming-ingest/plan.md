# Plan: Streaming Ingest

## Approach

Single `docker-compose.yml` at repo root. Python producer uses `confluent-kafka`
(or `kafka-python`) to publish JSON. One Kafka broker is enough for local dev.

## Architecture (this feature)

```text
producer (Python) --JSON--> Kafka topic: stock-ticks
                              ├── partition 0 (hash of symbols)
                              ├── partition 1
                              └── partition N
```

Use default partitioner with key = `symbol` so same symbol always maps to same
partition (ordering per symbol).

## Files to create

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Kafka + Zookeeper (or KRaft single node) |
| `src/common/config.py` | Read `KAFKA_BOOTSTRAP`, `TICK_INTERVAL_SEC` from env |
| `src/producer/main.py` | Synthetic generator + publish loop |
| `requirements.txt` | `confluent-kafka`, minimal deps |
| `.env.example` | Document env vars |

## Environment variables

| Var | Default | Description |
|-----|---------|-------------|
| `KAFKA_BOOTSTRAP` | `localhost:9092` | Broker address |
| `KAFKA_TOPIC` | `stock-ticks` | Topic name |
| `TICK_INTERVAL_SEC` | `1` | Seconds between ticks |
| `SYMBOLS` | `AAPL,MSFT,GOOGL,TSLA,AMZN` | Comma-separated |

## Synthetic price model

- Starting prices per symbol (hardcoded seeds, e.g. AAPL ≈ 180)
- Each tick: `price *= (1 + random.gauss(0, 0.001))` (simple random walk)
- Volume: random int 100–10000
- Side: random `buy` / `sell`
- Timestamp: `datetime.now(timezone.utc).isoformat()`

## Risks

| Risk | Mitigation |
|------|------------|
| Kafka slow to start | Producer retries connection with backoff |
| Port 9092 in use | Document in README; use compose port override |

## Alternatives (summary)

Full detail in ADR-002. RabbitMQ rejected for lack of replay.
