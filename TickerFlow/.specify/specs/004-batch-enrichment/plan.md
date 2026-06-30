# Plan: Batch Enrichment

## Approach

Airflow DAG with PythonOperator: list new raw Parquet since last run → pandas
or pyarrow aggregation per symbol → write enriched Parquet. Use same partition
layout as raw.

## Files to create / modify

| File | Purpose |
|------|---------|
| `dags/stock_enrichment_dag.py` | Scheduled enrichment DAG |
| `docker-compose.yml` | Add Airflow services |
| `requirements.txt` | `apache-airflow`, `pandas` (if needed) |

## Enriched schema (per symbol per window)

| Column | Description |
|--------|-------------|
| `symbol` | Ticker |
| `window_start` | Interval start UTC |
| `open` | First price in window |
| `high` | Max price |
| `low` | Min price |
| `close` | Last price |
| `volume` | Sum of volumes |

## Risks

| Risk | Mitigation |
|------|------------|
| Airflow heavy in Docker | Use `LocalExecutor`, limit parallelism |
