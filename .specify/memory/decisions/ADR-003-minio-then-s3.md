# ADR-003: MinIO locally, Amazon S3 on AWS

**Date:** 2026-06-30  
**Status:** accepted

## Context

The lake writer must persist Parquet files to object storage. We develop on a
laptop without AWS credentials or cost, then deploy the same code to AWS.

## Decision

Use **MinIO** locally (S3-compatible API). Use **Amazon S3** in AWS. Application
code uses `boto3` with endpoint URL from environment.

## Alternatives considered

| Option | Pros | Cons | Why rejected |
|--------|------|------|--------------|
| Local filesystem only | Zero setup | Different code path for AWS; no S3 API practice | Rewrite at deploy time |
| AWS S3 from day one | One environment | Cost, credentials, slow iteration | Bad dev experience |
| **MinIO → S3** | Same API, same code | Extra Docker container locally | **Chosen** |

## Consequences

- `S3_ENDPOINT` env var: `http://minio:9000` local, empty/default on AWS.
- Hive-style partitions (`symbol=`, `date=`) work identically on both.
- Glue catalog added only for Athena in spec 005.
