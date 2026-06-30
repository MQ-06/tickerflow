# Plan: Streaming Ingest

## Approach

Single `docker-compose.yml` at repo root. Python producer uses **`kafka-python`**
(pure Python, no `librdkafka` C dependency). One Kafka broker in **KRaft mode**
(no Zookeeper).

**Trade-off:** `kafka-python` has a lower throughput ceiling than `confluent-kafka`.
At ~1 tick/sec and 5 symbols that is irrelevant.

## Architecture (this feature)

```text
producer (Python) --JSON--> Kafka topic: stock-ticks (KRaft, 1 broker)
                              ├── partition 0
                              ├── partition 1
                              └── partition N
```

Partition key = `symbol` for per-symbol ordering.

## Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Kafka KRaft + healthcheck |
| `src/common/config.py` | Env-based settings |
| `src/producer/tick_generator.py` | Synthetic tick random walk |
| `src/producer/main.py` | Publish loop with Kafka retry |
| `requirements.txt` | `kafka-python==2.0.2` |
| `.env.example` | Documented env vars |
| `scripts/verify_spec001.py` | Automated e2e verification |

## Environment variables

| Var | Default | Description |
|-----|---------|-------------|
| `KAFKA_BOOTSTRAP` | `localhost:9092` | Broker address |
| `KAFKA_TOPIC` | `stock-ticks` | Topic name |
| `TICK_INTERVAL_SEC` | `1` | Seconds between ticks |
| `SYMBOLS` | `AAPL,MSFT,GOOGL,TSLA,AMZN` | Comma-separated |

## Alternatives (summary)

| Choice | Why this | Why not the other |
|--------|----------|-------------------|
| KRaft | Fewer containers, faster startup | Zookeeper is legacy overhead |
| kafka-python 2.0.2 | Pure Python, stable API | confluent-kafka needs native libs |

Full detail: [ADR-002](../../memory/decisions/ADR-002-kafka.md).
