# Athena query notes (spec 005)

DuckDB local scripts register a view named `ticks` over Parquet in S3/MinIO.
On AWS Athena, point the Glue external table `ticks` at `s3://<bucket>/raw/`
and run the same SQL bodies from this folder (no `read_parquet` in the query text).

Example Athena table (created by Terraform in spec 005):

```sql
SELECT symbol, ROUND(AVG(price), 2) AS avg_price
FROM ticks
GROUP BY symbol
ORDER BY symbol;
```

Files `avg_price_by_symbol.sql`, `latest_ticks.sql`, and `tick_count_by_symbol.sql`
are written for that table name and standard SQL only.
