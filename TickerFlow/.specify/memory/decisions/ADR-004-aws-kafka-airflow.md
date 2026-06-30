# ADR-004: EC2 + Docker for Kafka and Airflow on AWS

**Date:** 2026-06-30  
**Status:** accepted

## Context

Friday demo requires the pipeline on AWS. Managed options (MSK, MWAA) are
production-grade but slow to provision and expensive for a learning project.

## Decision

Run **Kafka, Airflow, producer, and consumer as Docker containers on one or
two `t3.small` EC2 instances**. Provision S3, Glue, Athena, IAM, and CloudWatch
via Terraform.

## Alternatives considered

| Option | Pros | Cons | Why rejected |
|--------|------|------|--------------|
| Amazon MSK | Fully managed Kafka | ~$70+/mo, 15–30 min provision | Overkill for 3-day demo |
| Amazon MWAA | Managed Airflow | ~$300+/mo minimum, slow setup | Cost and time |
| ECS/Fargate | More "cloud native" | More moving parts for solo build | Complexity vs. time |
| **EC2 + Docker Compose** | Same as local, fast to stand up, cheap | You manage the instance | **Chosen** for Friday timeline |

## Consequences

- `terraform apply` creates EC2 + S3 + Glue + Athena + CloudWatch.
- Deploy script copies `docker-compose.yml` (or AWS variant) to EC2.
- Lead story: "production would use MSK/MWAA; EC2 proves the architecture."
