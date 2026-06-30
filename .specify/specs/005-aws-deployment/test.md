# Tests: AWS Deployment

> Maps to acceptance criteria in [spec.md](spec.md). Requires local pipeline proven (001–004).

## Prerequisites

- AWS account with credentials configured (`aws sts get-caller-identity`)
- Terraform ≥ 1.5 installed
- Local pipeline passed all prior `test.md` sign-offs
- `infra/terraform/` and `scripts/deploy.sh` implemented

## Test matrix

| ID | Acceptance criterion | Type | Section |
|----|---------------------|------|---------|
| T1 | `terraform apply` no manual steps | Manual | §1 |
| T2 | Ticks in real S3 as Parquet | Manual | §2 |
| T3 | Athena query returns rows | Manual | §3 |
| T4 | CloudWatch logs visible | Manual | §4 |
| T5 | `terraform destroy` removes resources | Manual | §5 |
| T6 | Constitution done: local + AWS queryable | Manual | §6 |
| T7 | No app code changes vs local (env only) | Review | §7 |

---

## §1 — Terraform apply (T1)

**What:** Full stack provisions from code.

**How:**

```bash
cd infra/terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

**Pass if:**

- Exit code 0
- Outputs include S3 bucket name, EC2 host, Athena workgroup
- No resources created manually in AWS Console during apply

---

## §2 — Pipeline on AWS (T2)

**What:** Same producer/consumer, AWS env vars.

**How:**

```bash
./scripts/deploy.sh
./scripts/run_pipeline_aws.sh   # or SSH + docker compose on EC2
# wait 5+ minutes
aws s3 ls s3://<bucket>/raw/ --recursive
```

**Pass if:** `.parquet` objects under `raw/symbol=.../date=.../`.

---

## §3 — Athena query (T3)

**What:** Glue catalog + Athena work.

**How:** AWS Console → Athena → run:

```sql
SELECT symbol, COUNT(*) AS n, AVG(price) AS avg_price
FROM ticks
GROUP BY symbol;
```

(Use Glue table name from Terraform output.)

**Pass if:** `n > 0` for each symbol with data; `avg_price` plausible.

---

## §4 — CloudWatch (T4)

**What:** Logs reach AWS monitoring.

**How:**

```bash
aws logs describe-log-groups --log-group-name-prefix /tickerflow
aws logs tail /tickerflow/producer --since 10m
```

**Pass if:** Recent log events from producer and/or consumer.

---

## §5 — Terraform destroy (T5)

**What:** Reproducibility includes teardown.

**How:**

```bash
cd infra/terraform
terraform destroy
```

**Pass if:**

- Confirms destruction of EC2, S3 bucket (or empty + delete per design), Glue, etc.
- `aws s3 ls` shows bucket gone (or empty per destroy policy)
- No surprise charges left running (verify EC2 terminated)

> **Note:** Run destroy **after** demo rehearsal; re-`apply` before Friday if needed.

---

## §6 — Definition of done (T6)

**What:** Constitution requires **both** local and AWS.

**How:**

1. Run spec 003 `local_query.py` against local MinIO — pass
2. Run Athena query (§3) against AWS — pass

**Pass if:** Both return sensible data in the same session/day.

---

## §7 — Env-only swap (T7)

**What:** Proves decoupling from specs 001/002.

**How:** Diff env files only:

```bash
diff .env.example .env.aws.example
```

**Pass if:** Changes are limited to `KAFKA_BOOTSTRAP`, `S3_ENDPOINT`, `AWS_*`;
no diff in `src/producer/` or `src/consumer/` between local and AWS deploy.

---

## Pre-Friday rehearsal checklist

- [ ] Full apply → deploy → query → **do not destroy** until after demo
- [ ] IAM apply/destroy cycle tested once before presentation day
- [ ] Athena query saved in `queries/` for copy-paste during demo

---

## Sign-off

- [ ] T1–T7 passed
- [ ] Acceptance criteria in `spec.md` checked
- [ ] Update `masterplan.md` — spec 005 → ✅ Done
