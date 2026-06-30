# Spec: AWS Deployment

**Status:** draft  
**Depends on:** 001–004 working locally

## Problem

The Friday demo must run on real AWS — not just a laptop. Infrastructure must
be reproducible, tear-down-able, and match the local architecture.

## User story

As a data engineer presenting to my lead, I want `terraform apply` to provision
S3, Glue, Athena, EC2, and CloudWatch, then run the same pipeline code against
real AWS services.

## Scope

### In scope

- Terraform modules: S3, Glue catalog, Athena workgroup, EC2, IAM, CloudWatch
- Deploy script to copy code and start services on EC2
- Pipeline runs: producer → Kafka → consumer → S3
- Athena query returns rows
- CloudWatch log groups for producer/consumer
- `terraform destroy` documented

### Out of scope

- MSK, MWAA (see ADR-004)
- CI/CD pipeline
- Multi-AZ HA

## Acceptance criteria

- [ ] `terraform apply` succeeds without manual console clicks
- [ ] Ticks land in real S3 bucket
- [ ] Athena `SELECT count(*) FROM ticks` returns > 0
- [ ] CloudWatch shows recent log events
- [ ] `terraform destroy` removes billable resources

## References

- [ADR-003](../../memory/decisions/ADR-003-minio-then-s3.md)
- [ADR-004](../../memory/decisions/ADR-004-aws-kafka-airflow.md)
