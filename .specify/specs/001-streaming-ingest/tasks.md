# Tasks: Streaming Ingest

- [ ] Create `requirements.txt` with `kafka-python`
- [ ] Create `src/common/config.py` — load env vars
- [ ] Create `src/producer/main.py` — synthetic tick loop + Kafka publish with retry
- [ ] Create `docker-compose.yml` — Kafka KRaft (no Zookeeper) + healthcheck
- [ ] Create `.env.example` with all env vars documented
- [ ] Run `docker compose up -d`; wait until Kafka healthcheck passes
- [ ] Run producer; confirm logs show ticks
- [ ] Run `kafka-console-consumer`; confirm JSON for all 5 symbols within 30s
- [ ] Stop producer, restart it; confirm publishing resumes without manual cleanup
- [ ] Tick all acceptance criteria in `spec.md`
- [ ] Update `masterplan.md` — spec 001 status → ✅ Done
