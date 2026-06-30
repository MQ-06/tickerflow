import os
from dataclasses import dataclass


DEFAULT_SYMBOLS = ("AAPL", "MSFT", "GOOGL", "TSLA", "AMZN")


@dataclass(frozen=True)
class ProducerConfig:
    kafka_bootstrap: str
    kafka_topic: str
    tick_interval_sec: float
    symbols: tuple[str, ...]


@dataclass(frozen=True)
class ConsumerConfig:
    kafka_bootstrap: str
    kafka_topic: str
    kafka_group_id: str
    s3_endpoint: str
    s3_bucket: str
    aws_access_key_id: str
    aws_secret_access_key: str
    batch_size: int
    batch_flush_sec: float


def load_producer_config() -> ProducerConfig:
    symbols_raw = os.getenv("SYMBOLS", ",".join(DEFAULT_SYMBOLS))
    symbols = tuple(s.strip().upper() for s in symbols_raw.split(",") if s.strip())

    return ProducerConfig(
        kafka_bootstrap=os.getenv("KAFKA_BOOTSTRAP", "localhost:9092"),
        kafka_topic=os.getenv("KAFKA_TOPIC", "stock-ticks"),
        tick_interval_sec=float(os.getenv("TICK_INTERVAL_SEC", "1")),
        symbols=symbols or DEFAULT_SYMBOLS,
    )


def load_consumer_config() -> ConsumerConfig:
    return ConsumerConfig(
        kafka_bootstrap=os.getenv("KAFKA_BOOTSTRAP", "localhost:9092"),
        kafka_topic=os.getenv("KAFKA_TOPIC", "stock-ticks"),
        kafka_group_id=os.getenv("KAFKA_GROUP_ID", "tickerflow-consumer"),
        s3_endpoint=os.getenv("S3_ENDPOINT", "http://localhost:9000"),
        s3_bucket=os.getenv("S3_BUCKET", "stock-lake"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "minioadmin"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin"),
        batch_size=int(os.getenv("BATCH_SIZE", "10")),
        batch_flush_sec=float(os.getenv("BATCH_FLUSH_SEC", "30")),
    )

