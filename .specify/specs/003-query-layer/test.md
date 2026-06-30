# Tests: Query Layer

> Maps to acceptance criteria in [spec.md](spec.md). Requires spec 002 data in lake.

## Prerequisites

- Producer + consumer ran ≥ 5 minutes (data in `raw/`)
- `scripts/local_query.py` and `queries/*.sql` implemented

## Test matrix

| ID | Acceptance criterion | Type | Section |
|----|---------------------|------|---------|
| T1 | `local_query.py` runs all demo queries | Manual | §1 |
| T2 | Latest tick per symbol → 5 rows | Manual | §2 |
| T3 | Average price plausible vs seeds | Manual | §3 |
| T4 | Tick count > 0 | Manual | §4 |
| T5 | SQL files exist in `queries/` | Manual | §5 |
| T6 | Empty lake handled gracefully | Manual | §6 |

---

## §1 — Script runs (T1)

**What:** Entry point executes without error.

**How:**

```bash
python scripts/local_query.py
# or per-query:
python scripts/local_query.py --query queries/avg_price_by_symbol.sql
```

**Pass if:** All bundled queries print a table to stdout; exit code 0.

---

## §2 — Latest tick per symbol (T2)

**What:** Exactly one row per constitution symbol.

**How:** Run `queries/latest_ticks.sql` via script.

**Pass if:**

- Result has **5 rows**
- Symbols = `AAPL`, `MSFT`, `GOOGL`, `TSLA`, `AMZN` (each once)
- `timestamp` is recent (within last few minutes of test run)

---

## §3 — Average price sanity (T3)

**What:** Averages are in a plausible range (not 0, not negative).

**How:** Run `queries/avg_price_by_symbol.sql`.

**Pass if:** Each symbol's `avg_price` is > 0 and within ~50% of producer seed
(e.g. AAPL seed ~180 → avg roughly 90–270 after random walk).

---

## §4 — Tick count (T4)

**What:** Data actually flowed into the lake.

**How:** Run count query (or `SELECT count(*) ...` in script).

**Pass if:** Total tick count ≥ number of minutes producer ran × ~1 tick/sec
(order of magnitude check, not exact).

---

## §5 — Query files present (T5)

**What:** Demo SQL is versioned and readable.

**How:**

```bash
ls queries/
cat queries/avg_price_by_symbol.sql
cat queries/latest_ticks.sql
```

**Pass if:** Files exist; SQL is valid ANSI (no DuckDB-only syntax unless documented).

---

## §6 — Empty lake (T6)

**What:** Script fails gracefully with no data.

**How:** Point script at empty path or fresh bucket; run once.

**Pass if:** Prints human-readable message ("no data found"); exit code ≠ unhandled exception.

---

## Athena parity check (prep for spec 005)

**What:** Same SQL works on AWS later.

**How:** Copy `queries/avg_price_by_symbol.sql` text; confirm no DuckDB-only
functions (`read_parquet` path syntax differs — table name swap only on AWS).

**Pass if:** Query body uses standard `SELECT`, `GROUP BY`, `AVG`, `MAX` only.

---

## Sign-off

- [x] T1–T6 passed
- [x] Acceptance criteria in `spec.md` checked
- [x] Update `masterplan.md` — spec 003 → ✅ Done
