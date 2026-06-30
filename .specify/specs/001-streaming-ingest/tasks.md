# Tasks: Streaming Ingest

- [ ] Create `requirements.txt` with `confluent-kafka`
- [ ] Create `src/common/config.py` — load env vars
- [ ] Create `src/producer/main.py` — synthetic tick loop + Kafka publish
- [ ] Create `docker-compose.yml` — Kafka (+ Zookeeper or KRaft)
- [ ] Create `.env.example` with all env vars documented
- [ ] Run `docker compose up -d` and wait for Kafka healthy
- [ ] Run producer; confirm logs show ticks
- [ ] Run `kafka-console-consumer` and see JSON for all 5 symbols
- [ ] Tick all acceptance criteria in `spec.md`
- [ ] Update `masterplan.md` — spec 001 status → ✅ Done
