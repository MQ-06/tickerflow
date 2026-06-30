# Spec: Demo Presentation

**Status:** draft  
**Depends on:** 001, 002, 003, 004, 005 (constitution definition of done)

## Problem

A working pipeline is not the same as a successful demo. Without a script and
fallback plan, live presentations fail for presentation reasons — losing track
of what to show next, or a live AWS hiccup derailing the whole thing.

## User story

As a data engineer, I want a clear demo script and fallback plan so I can walk
my lead through the system confidently and recover smoothly if something does
not behave live.

## Scope

### In scope

- Demo script: order of what to show, what to say, which terminal/UI open at each step
- One-line "why this, not X" per major tool — pulled from ADRs, not improvised
- Fallback assets: screenshots or short clips per stage if live AWS fails
- Local-only backup path rehearsed (same Docker stack, no internet required)
- README section summarizing the project for repo readers after the demo
- Target runtime: under 15 minutes for full walkthrough

### Out of scope

- Slide deck (terminal + Airflow UI + Athena console is the demo)
- Exhaustive Q&A prep beyond ADR talking points

## Inputs / outputs

| Step | Input | Output |
|------|-------|--------|
| Script | All specs + ADRs | Ordered walkthrough in `plan.md` |
| Fallback | Working pipeline runs | Screenshots/clips per stage |
| README | Project state | `README.md` summary section |

## Acceptance criteria

- [ ] Demo script exists in `plan.md`; dry-run completed start to finish at least once
- [ ] Every stack component has a one-line "why this, not X" ready (Kafka, Pydantic, Parquet, S3, Athena, Airflow, Terraform, CloudWatch)
- [ ] Fallback assets exist and work without live AWS
- [ ] Full demo (local + AWS) completes in under 15 minutes
- [ ] Constitution definition of done verified live before presentation: local pipeline **and** AWS queryable

## Risks

| Risk | Mitigation |
|------|------------|
| Live AWS fails in front of lead | Fallback screenshots; rehearsed local-only path |
| Running long mid-explanation | Script has a "skip to" point per stage |

## References

- [masterplan.md](../../masterplan.md) — phase status
- [Constitution](../../memory/constitution.md) — definition of done (demo)
- All ADRs in [memory/decisions/](../../memory/decisions/) — source of "why" talking points
