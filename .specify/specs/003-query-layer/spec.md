# Spec: Query Layer

**Status:** draft  
**Depends on:** 002-validation-lake

## Problem

Data sitting in Parquet files is not useful until someone can ask questions of
it. Loading into a traditional database first adds cost and latency that
ad-hoc analytical queries do not need.

## User story

As a data engineer (and as my lead watching the demo), I want to run plain
SQL directly against the lake so I can verify data is flowing and answer
questions like "what is AAPL's average price today" without an ETL step.

## Scope

### In scope

- DuckDB queries against local Parquet files (path strategy decided in `plan.md`:
  read from MinIO mount, S3-compatible path, or synced local copy)
- Example queries: latest tick per symbol, average price by symbol, tick count by symbol
- `scripts/local_query.py` to run queries on demand and print table output
- SQL kept to ANSI subset that DuckDB and Athena both support (eases spec 005)

### Out of scope

- Athena / Glue setup (spec 005)
- Query performance tuning or indexing
- UI or dashboard — terminal output is sufficient

## Inputs / outputs

| Step | Input | Output |
|------|-------|--------|
| Query | SQL + path to Parquet lake | Result rows (printed table) |

## Acceptance criteria

- [ ] `scripts/local_query.py` runs each example query against live data from spec 002 and returns sensible results
- [ ] "Latest tick per symbol" returns exactly 5 rows (one per constitution symbol)
- [ ] Average price per symbol returns plausible values within the random-walk seed range from spec 001
- [ ] Tick count query returns > 0 after producer has run for at least 2 minutes

## Risks

| Risk | Mitigation |
|------|------------|
| DuckDB SQL diverges from Athena syntax | Stick to standard ANSI SQL both engines support |
| No data in lake yet | Script prints a clear message instead of crashing |

## References

- [Constitution](../../memory/constitution.md) — tech stack (DuckDB local / Athena AWS)
