# Spec: Demo Presentation

**Status:** draft  
**Depends on:** 005-aws-deployment (or fallback: local-only if AWS slips)

## Problem

A working pipeline is not enough for Friday. The lead needs to see end-to-end
flow and understand **why** each choice was made.

## User story

As a presenter, I want a rehearsed 15-minute demo with talking points, backup
plans, and three "why not X?" answers ready.

## Scope

### In scope

- Ordered demo script (what to click, what to say)
- Architecture diagram reference
- 3 prepared ADR talking points
- Fallback if AWS fails (show local + explain Terraform ready)
- Pre-demo checklist

### Out of scope

- Slides deck (optional)

## Acceptance criteria

- [ ] Demo script run-through completes in under 20 minutes
- [ ] Every step has a one-sentence "why this matters"
- [ ] Fallback path tested once

## References

- All ADRs in `memory/decisions/`
