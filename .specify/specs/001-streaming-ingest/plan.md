# Plan: Streaming Ingest

## Approach

Single `docker-compose.yml` at repo root. Python producer uses **`kafka-python`**
(pure Python, no `librdkafka` C dependency). One Kafka broker in **KRaft mode**
(no Zookeeper — fewer containers, faster local startup).

**Trade-off:** `kafka-python` has a lower throughput ceiling than `confluent-kafka`.
At our scale (~1 tick/sec, 5 symbols) that is irrelevant and avoids mid-build
native dependency issues.

## Architecture (this feature)

```text
producer (Python) --JSON--> Kafka topic: stock-ticks (KRaft, 1 broker)
                              ├── partition 0
                              ├── partition 1
                              └── partition N
```

Partition key = `symbol` so the same symbol always maps to the same partition
(ordering per symbol).

## Files to create

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Kafka (KRaft) with **healthcheck** so dependent steps wait for readiness |
| `src/common/config.py` | Read `KAFKA_BOOTSTRAP`, `TICK_INTERVAL_SEC` from env |
| `src/producer/main.py` | Synthetic generator + publish loop with connection retry |
| `requirements.txt` | `kafka-python`, minimal deps |
| `.env.example` | Document env vars |

## Docker Compose notes

- Use `apache/kafka` or `confluentinc/cp-kafka` image with KRaft env vars
  (`KAFKA_PROCESS_ROLES`, `KAFKA_NODE_ID`, etc.) — no Zookeeper service
- Healthcheck: `kafka-broker-api-versions` or `kafka-topics --list` against
  `localhost:9092` with `interval` / `retries` so `depends_on: condition: service_healthy` works

## Environment variables

| Var | Default | Description |
|-----|---------|-------------|
| `KAFKA_BOOTSTRAP` | `localhost:9092` | Broker address |
| `KAFKA_TOPIC` | `stock-ticks` | Topic name |
| `TICK_INTERVAL_SEC` | `1` | Seconds between ticks |
| `SYMBOLS` | `AAPL,MSFT,GOOGL,TSLA,AMZN` | Comma-separated (constitution list) |

## Synthetic price model

- Starting prices per symbol (hardcoded seeds, e.g. AAPL ≈ 180)
- Each tick: `price *= (1 + random.gauss(0, 0.001))` (simple random walk)
- Volume: random int 100–10000
- Side: random `buy` / `sell`
- Timestamp: `datetime.now(timezone.utc).isoformat()`

## Risks

| Risk | Mitigation |
|------|------------|
| Kafka slow to start | Healthcheck + producer backoff retry |
| Port 9092 in use | Document in README; compose port override |

## Alternatives (summary)

| Choice | Why this | Why not the other |
|--------|----------|-------------------|
| KRaft | Fewer containers, modern default | Zookeeper adds ops overhead for no demo benefit |
| kafka-python | Pure Python, easy local dev | confluent-kafka needs librdkafka; overkill at 1 tick/sec |

Full broker rationale: [ADR-002](../../memory/decisions/ADR-002-kafka.md).
