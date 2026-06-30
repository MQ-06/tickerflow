# Plan: Query Layer

## Approach

DuckDB reads Parquet directly (`read_parquet('path/**/*.parquet')`). For MinIO,
either sync files locally or use DuckDB httpfs with S3-compatible settings.

## Files to create

| File | Purpose |
|------|---------|
| `queries/avg_price_by_symbol.sql` | Demo query 1 |
| `queries/latest_ticks.sql` | Demo query 2 |
| `scripts/local_query.py` | Run queries, print table |

## Local vs AWS SQL

DuckDB and Athena both use standard SQL. Table/column names should match Glue
catalog definitions created in spec 005.

## Risks

| Risk | Mitigation |
|------|------------|
| No data yet | Script prints friendly message if empty |
