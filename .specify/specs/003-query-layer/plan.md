# Plan: Query Layer

## Approach

DuckDB with `httpfs` reads Parquet directly from MinIO (`s3://stock-lake/raw/**/*.parquet`).
SQL files use table name `ticks` (view registered by `local_query.py`). Same SQL
bodies work on Athena in spec 005 against Glue table `ticks`.

## Files

| File | Purpose |
|------|---------|
| `src/query/lake_connection.py` | DuckDB + S3/MinIO setup, `ticks` view |
| `scripts/local_query.py` | Run demo queries, print tables |
| `queries/*.sql` | Athena-compatible SQL |
| `queries/README.md` | Athena parity notes |
| `scripts/verify_spec003.py` | Automated e2e checks |

## Environment variables

Reuses lake config from spec 002: `S3_ENDPOINT`, `S3_BUCKET`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`.

## Risks

| Risk | Mitigation |
|------|------------|
| No data yet | Friendly message + exit 1 |
| Empty glob in tests | `--parquet-glob` override |
