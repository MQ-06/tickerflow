# Tests: Demo Presentation

> Maps to acceptance criteria in [spec.md](spec.md). Meta-tests for the presentation itself.

## Prerequisites

- Specs 001–005 sign-offs complete (or fallback path ready)
- `plan.md` demo script written
- Fallback screenshots/clips captured

## Test matrix

| ID | Acceptance criterion | Type | Section |
|----|---------------------|------|---------|
| T1 | Dry-run under 15 minutes | Manual | §1 |
| T2 | Every step has "why" line | Review | §2 |
| T3 | "Why not X?" answers ready | Review | §3 |
| T4 | Fallback works without AWS | Manual | §4 |
| T5 | Constitution done verified live | Manual | §5 |
| T6 | README summary exists | Review | §6 |

---

## §1 — Timed dry-run (T1)

**What:** Full script fits presentation slot.

**How:**

1. Open `plan.md` demo script
2. Run every step live (local + AWS) with a timer
3. Record total time

**Pass if:** ≤ 15 minutes (20 min hard stop per spec).

**Skip-to test:** From mid-script, jump to Athena query step only — still coherent in < 5 min.

---

## §2 — "Why" per step (T2)

**What:** Not just clicks — rationale ready.

**How:** For each demo step in `plan.md`, confirm a **Say** column exists with
one sentence tying to problem solved.

| Step | Must mention |
|------|----------------|
| Kafka | decoupling / buffer |
| Pydantic | bad data gate |
| Parquet + S3 | cheap analytics storage |
| Athena | SQL without warehouse load |
| Airflow | batch vs stream |
| Terraform | reproducible infra |
| CloudWatch | detect failure early |

**Pass if:** All rows filled; no empty **Say** cells.

---

## §3 — ADR talking points (T3)

**What:** Three "why not X?" without improvising.

**How:** Read aloud from ADRs (30 sec each):

1. [ADR-001](../../memory/decisions/ADR-001-synthetic-data.md) — synthetic vs API
2. [ADR-002](../../memory/decisions/ADR-002-kafka.md) — Kafka vs RabbitMQ/Kinesis
3. [ADR-003](../../memory/decisions/ADR-003-minio-then-s3.md) or [ADR-004](../../memory/decisions/ADR-004-aws-kafka-airflow.md)

**Pass if:** You can explain each in one sentence without opening the file live.

---

## §4 — Fallback path (T4)

**What:** AWS outage does not kill the demo.

**How:**

1. Disconnect network or block AWS endpoints (or simulate)
2. Run local-only path: `docker compose up` → producer → consumer → `local_query.py`
3. Show pre-captured screenshots for AWS steps

**Pass if:** Lead still sees end-to-end data flow locally + static proof of AWS deploy.

---

## §5 — Live definition of done (T5)

**What:** Constitution — both environments queryable **before** walking into demo.

**How:** Morning of presentation:

```bash
# Local
python scripts/local_query.py

# AWS
# Athena query from spec 005 test §3
```

**Pass if:** Both return data. If AWS fails, explicit decision: local demo + fallback assets (document in plan.md).

---

## §6 — README (T6)

**What:** Repo stands alone after demo.

**How:**

```bash
grep -E "TickerFlow|Architecture|Quick start" README.md
```

**Pass if:** README has: what it is, architecture one-liner, how to run locally,
link to `.specify/masterplan.md`.

---

## Pre-demo day-of checklist

- [ ] Producer + consumer running 10 min before
- [ ] Browser tabs: Airflow UI, Athena, CloudWatch, MinIO (local backup)
- [ ] `terraform output` values copied for quick reference
- [ ] Phone hotspot tested if venue WiFi unreliable

---

## Sign-off

- [ ] T1–T6 passed
- [ ] Acceptance criteria in `spec.md` checked
- [ ] Update `masterplan.md` — spec 006 → ✅ Done
