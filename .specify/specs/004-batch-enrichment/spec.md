# Spec: Batch Enrichment

**Status:** draft  
**Depends on:** 002-validation-lake, 003-query-layer (queries can reference enriched later)

## Problem

Some metrics (OHLC, moving averages) need a window of historical ticks. Computing
them on every single tick is wasteful. They belong on a schedule over accumulated
lake data.

## User story

As a data engineer, I want Airflow to run every 15 minutes, read raw Parquet,
compute per-symbol OHLC and volume, and write enriched Parquet so analysts can
query summaries without scanning every tick.

## Scope

### In scope

- Airflow in Docker Compose (webserver + scheduler)
- DAG `stock_enrichment` on 15-minute schedule
- Read `raw/`, write `enriched/` with OHLC columns
- Airflow UI shows successful runs

### Out of scope

- Complex dependencies across external systems
- Real-time stream processing (Flink/Spark Streaming)

## Acceptance criteria

- [ ] Airflow UI accessible at `localhost:8080`
- [ ] DAG run succeeds (green)
- [ ] `enriched/` contains Parquet with open, high, low, close, volume columns
- [ ] DuckDB can query enriched table

## References

- Constitution — enriched path pattern
