# ADR-001: Synthetic tick data instead of a live market API

**Date:** 2026-06-30  
**Status:** accepted

## Context

The pipeline needs a continuous stream of realistic stock ticks. Free market
APIs (Finnhub, Alpha Vantage, Twelve Data) require keys, impose rate limits,
and can fail during a live presentation.

## Decision

Use a **Python synthetic tick generator** (geometric Brownian motion per symbol)
as the sole data source for v1. Seed each symbol with a realistic starting
price. Optionally document how to swap in a real API later (producer-only change).

## Alternatives considered

| Option | Pros | Cons | Why rejected |
|--------|------|------|--------------|
| Live WebSocket API | "Real" data | Keys, rate limits, network risk on demo day | Unreliable for Friday presentation |
| yfinance polling | Free, no key | ~15 min delay, not true streaming, ToS grey area | Not a real-time demo story |
| Static CSV replay | Deterministic | Not continuous; feels fake in a "live" demo | Poor narrative for streaming architecture |
| **Synthetic generator** | Always works, controllable volume, realistic shape | Not real market data | **Chosen** — reliability wins for demo |

## Consequences

- Producer owns all randomness; downstream is unaware.
- Lead may ask "is this real?" — answer honestly: synthetic for reliability,
  architecture is identical for a real feed.
- ADR stands until a real API integration spec is written.
