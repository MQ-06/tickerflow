# Spec: Query Layer

**Status:** done  
**Depends on:** 002-validation-lake

## Problem

Data in the lake is useless if nobody can ask questions. We need SQL access
without loading data into a traditional database.

## User story

As an analyst (or lead in a demo), I want to run SQL against stored ticks so I
can see averages, counts, and latest prices per symbol.

## Scope

### In scope

- Saved SQL query files for demo
- Local query script using DuckDB over Parquet (MinIO via httpfs)
- Queries: avg price by symbol, tick count, latest price per symbol
- Athena parity notes in `queries/README.md` (spec 005)

### Out of scope

- BI dashboards
- Glue/Athena setup (spec 005)

## Acceptance criteria

- [x] `scripts/local_query.py` runs demo queries and prints results
- [x] Results match known data after producer has run 5+ minutes
- [x] SQL files live in `queries/` and are readable in demo

## References

- Constitution — partition paths
