# Spec: AWS Deployment

**Status:** draft  
**Depends on:** 001, 002, 003, 004 (entire local pipeline working first)

## Problem

A pipeline that only runs on a laptop is not a credible cloud data engineering
demo. Every piece must exist in AWS, provisioned reproducibly — not clicked
together in the console.

## User story

As a data engineer presenting to my lead, I want the entire pipeline running
in real AWS, provisioned by Terraform, so the demo proves this is not just a
local toy.

## Scope

### In scope

- Terraform: S3 bucket (replaces MinIO), Glue catalog, Athena workgroup
- Terraform: EC2 running Kafka (KRaft, Docker) + Airflow + pipeline services
  (per [ADR-004](../../memory/decisions/ADR-004-aws-kafka-airflow.md))
- Config swap only — `KAFKA_BOOTSTRAP`, S3 endpoint, and credentials via env;
  **no application code changes** (validates decoupling from specs 001/002)
- CloudWatch log groups for producer and consumer
- `scripts/deploy.sh` — `terraform apply` + deploy stack to EC2
- `terraform destroy` documented and tested once before Friday

### Out of scope

- Auto-scaling, multi-AZ, high availability
- CI/CD for infrastructure
- MSK / MWAA (ADR-004: EC2 + Docker for speed and cost)
- Cost optimization beyond small / free-tier-eligible instance types

## Inputs / outputs

| Step | Input | Output |
|------|-------|--------|
| Provision | Terraform config | S3, Glue, Athena, EC2, IAM, CloudWatch |
| Deploy | Docker images + EC2 | Running Kafka + Airflow + producer/consumer in cloud |
| Verify | Athena SQL | Same logical results as local DuckDB against cloud data |

## Acceptance criteria

- [ ] `terraform apply` succeeds with no manual console steps
- [ ] Producer (AWS env) publishes ticks that land in real S3 as Parquet
- [ ] Athena query against Glue-cataloged table returns correct results
- [ ] CloudWatch shows recent log events from pipeline services
- [ ] `terraform destroy` cleanly tears down all billable resources
- [ ] Constitution definition of done met: local **and** AWS both queryable

## Risks

| Risk | Mitigation |
|------|------------|
| AWS costs if left running | `terraform destroy` after demo; smallest viable instances |
| IAM errors mid-demo | Full apply/destroy cycle tested at least once before Friday |
| Networking issues eat last evening | Start this phase Thursday morning, not Friday AM |

## References

- [ADR-003](../../memory/decisions/ADR-003-minio-then-s3.md) — same boto3 code, different endpoint
- [ADR-004](../../memory/decisions/ADR-004-aws-kafka-airflow.md) — EC2 vs MSK/MWAA
- [Constitution](../../memory/constitution.md) — local-first-then-AWS, demo definition of done
