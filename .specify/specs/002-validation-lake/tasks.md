# Tasks: Validation & Lake Storage

- [x] Add Pydantic `Tick` model in `src/common/models/tick.py`
- [x] Add MinIO to `docker-compose.yml`
- [x] Implement `src/consumer/writer.py` (Parquet + quarantine)
- [x] Implement `src/consumer/main.py` (consume, validate, batch, write)
- [x] Inject one bad tick manually; confirm quarantine path
- [x] Confirm Parquet files in `raw/symbol=AAPL/date=…/`
- [x] Run all checks in [test.md](test.md); sign off
- [x] Tick acceptance criteria in `spec.md`
- [x] Update `masterplan.md` — spec 002 → ✅ Done
