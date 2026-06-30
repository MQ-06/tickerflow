# Plan: Demo Presentation

## Demo script (~15 min)

| # | Time | Action | Say |
|---|------|--------|-----|
| 1 | 2 min | Show architecture (masterplan or diagram) | "Two speeds: stream for ingest, batch for enrichment" |
| 2 | 2 min | Show `terraform apply` output or state | "Entire AWS stack is reproducible from code" |
| 3 | 3 min | Live producer → Kafka → consumer → S3 | "Producer doesn't know about storage; Kafka decouples them" |
| 4 | 2 min | Athena query: avg price by symbol | "No warehouse load — SQL directly on Parquet in S3" |
| 5 | 3 min | Airflow UI → trigger DAG → show enriched | "OHLC needs history; that's batch, not stream" |
| 6 | 2 min | CloudWatch log tail | "We'd know before users if validation started failing" |
| 7 | 1 min | Open ADR-001 | "Synthetic data for reliability; swap producer only for real feed" |

## "Why not X?" cheat sheet

| Question | Answer |
|----------|--------|
| Why not Postgres? | Wrong for append-only analytics at scale; lake is cheaper |
| Why not Kinesis? | Kafka = replayable log; skills transfer; same local/AWS story |
| Why not Spark Streaming? | Heavier ops; Python consumer enough at this volume |

## Fallback plan

If AWS is down: run local Docker demo, show Terraform code, explain "same
containers on EC2."

## Pre-demo checklist

- [ ] Producer + consumer running 10 min before (data in lake)
- [ ] Athena query tested morning of
- [ ] Airflow DAG green
- [ ] Browser tabs pre-opened
- [ ] `terraform destroy` scheduled post-demo
