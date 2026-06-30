# Plan: AWS Deployment

## Approach

Terraform in `infra/terraform/`. One EC2 instance runs Docker Compose with Kafka,
Airflow, producer, consumer. S3 holds the lake. Glue external table points at
`s3://stock-lake/raw/`. Athena queries via workgroup.

## Files to create

| File | Purpose |
|------|---------|
| `infra/terraform/main.tf` | Provider, backend |
| `infra/terraform/variables.tf` | Region, bucket name, instance type |
| `infra/terraform/s3.tf` | Lake bucket |
| `infra/terraform/glue_athena.tf` | Table + workgroup |
| `infra/terraform/ec2.tf` | Instance + security group |
| `infra/terraform/iam.tf` | EC2 role for S3 access |
| `infra/terraform/cloudwatch.tf` | Log groups |
| `scripts/deploy.sh` | Apply + SSH/copy/start |
| `scripts/run_pipeline_aws.sh` | Start producer/consumer on EC2 |

## Environment switch

| Var | Local | AWS |
|-----|-------|-----|
| `S3_ENDPOINT` | `http://minio:9000` | (unset — real S3) |
| `KAFKA_BOOTSTRAP` | `localhost:9092` | EC2 internal host |

## Risks

| Risk | Mitigation |
|------|------------|
| EC2 SG blocks Kafka | Document ports; restrict to demo IPs |
| AWS costs | `t3.small`, destroy after demo |
