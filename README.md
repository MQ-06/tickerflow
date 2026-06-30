# TickerFlow

Real-time stock tick pipeline: Kafka → validation → Parquet lake → SQL → Airflow enrichment.

**Specs:** see [`.specify/masterplan.md`](.specify/masterplan.md)

## Quick start (spec 001 — streaming ingest)

```bash
# 1. Start Kafka (KRaft)
docker compose up -d

# 2. Install Python deps
pip install -r requirements.txt

# 3. Run producer
python -m src.producer.main

# 4. Verify (separate terminal, with producer running)
python scripts/verify_spec001.py

# 5. Or inspect manually
docker compose exec kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 --topic stock-ticks --from-beginning --timeout-ms 10000
```

Copy `.env.example` to `.env` to override `KAFKA_BOOTSTRAP`, `TICK_INTERVAL_SEC`, etc.

## Tests

```bash
pytest tests/unit -q
```
