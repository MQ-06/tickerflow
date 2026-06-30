# Tasks: Validation & Data Lake

- [ ] Add Pydantic `Tick` model in `src/common/models/tick.py`
- [ ] Add MinIO to `docker-compose.yml`
- [ ] Implement `src/consumer/writer.py` (Parquet + quarantine)
- [ ] Implement `src/consumer/main.py` (consume, validate, batch, write)
- [ ] Inject one bad tick manually; confirm quarantine path
- [ ] Confirm Parquet files in `raw/symbol=AAPL/date=…/`
- [ ] Run all checks in [test.md](test.md); sign off
- [ ] Tick acceptance criteria in `spec.md`
- [ ] Update `masterplan.md` — spec 002 → ✅ Done
