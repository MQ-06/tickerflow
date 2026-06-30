# Plan: Validation & Data Lake

## Approach

Long-running Python consumer: poll Kafka → validate with Pydantic → accumulate
batch (e.g. 100 ticks or 30 seconds) → write one Parquet file per batch.
File name includes timestamp to avoid overwrites on restart.

## Files to create / modify

| File | Purpose |
|------|---------|
| `src/common/models/tick.py` | Pydantic `Tick` model |
| `src/consumer/main.py` | Kafka consume + validate + route |
| `src/consumer/writer.py` | Parquet + quarantine writers (boto3) |
| `docker-compose.yml` | Add MinIO service |
| `requirements.txt` | Add `pydantic`, `pyarrow`, `boto3` |

## Environment variables

| Var | Default | Description |
|-----|---------|-------------|
| `S3_ENDPOINT` | `http://localhost:9000` | MinIO URL |
| `S3_BUCKET` | `stock-lake` | Lake bucket |
| `AWS_ACCESS_KEY_ID` | `minioadmin` | MinIO creds |
| `AWS_SECRET_ACCESS_KEY` | `minioadmin` | MinIO creds |
| `BATCH_SIZE` | `100` | Ticks per Parquet file |

## Risks

| Risk | Mitigation |
|------|------------|
| Duplicate files on restart | Unique filename per batch (`ticks_{uuid}.parquet`) |
| MinIO not ready | Retry bucket creation with backoff |
