import os
from dataclasses import dataclass


DEFAULT_SYMBOLS = ("AAPL", "MSFT", "GOOGL", "TSLA", "AMZN")


@dataclass(frozen=True)
class ProducerConfig:
    kafka_bootstrap: str
    kafka_topic: str
    tick_interval_sec: float
    symbols: tuple[str, ...]


def load_producer_config() -> ProducerConfig:
    symbols_raw = os.getenv("SYMBOLS", ",".join(DEFAULT_SYMBOLS))
    symbols = tuple(s.strip().upper() for s in symbols_raw.split(",") if s.strip())

    return ProducerConfig(
        kafka_bootstrap=os.getenv("KAFKA_BOOTSTRAP", "localhost:9092"),
        kafka_topic=os.getenv("KAFKA_TOPIC", "stock-ticks"),
        tick_interval_sec=float(os.getenv("TICK_INTERVAL_SEC", "1")),
        symbols=symbols or DEFAULT_SYMBOLS,
    )
