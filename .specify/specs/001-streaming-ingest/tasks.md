# Tasks: Streaming Ingest

- [x] Create `requirements.txt` with `kafka-python==2.0.2`
- [x] Create `src/common/config.py` — load env vars
- [x] Create `src/producer/tick_generator.py` + `src/producer/main.py`
- [x] Create `docker-compose.yml` — Kafka KRaft + healthcheck
- [x] Create `.env.example` with all env vars documented
- [x] Run `docker compose up -d`; wait until Kafka healthcheck passes
- [x] Run producer; confirm logs show ticks
- [x] Run `kafka-console-consumer` / `scripts/verify_spec001.py` — all 5 symbols
- [x] Stop and restart producer; confirm publishing resumes without cleanup
- [x] Run all checks in [test.md](test.md); sign off
- [x] Tick all acceptance criteria in `spec.md`
- [x] Update `masterplan.md` — spec 001 status → ✅ Done
