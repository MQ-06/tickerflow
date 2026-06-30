# TickerFlow

Real-time stock tick pipeline: Kafka → validation → Parquet lake → SQL → Airflow enrichment.

**Specs:** see [`.specify/masterplan.md`](.specify/masterplan.md)

## Quick start (spec 001 — streaming ingest)

```bash
docker compose up -d
pip install -r requirements.txt
python -m src.producer.main
python scripts/verify_spec001.py
```

## Quick start (spec 002 — validation & lake)

```bash
docker compose up -d          # Kafka + MinIO
pip install -r requirements.txt

# Terminal 1 — producer
python -m src.producer.main

# Terminal 2 — consumer
python -m src.consumer.main

# Terminal 3 — verify (or self-contained):
python scripts/verify_spec002.py
```

MinIO console: http://localhost:9001 (`minioadmin` / `minioadmin`)

Copy `.env.example` to `.env` to override endpoints and batch settings.

## Tests

```bash
pytest tests/unit -q
```
