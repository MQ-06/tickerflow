import json
import logging
import sys
import time

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

from src.common.config import load_producer_config
from src.producer.tick_generator import TickGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


def create_producer(
    bootstrap: str, max_retries: int = 30, delay_sec: float = 2.0
) -> KafkaProducer:
    """Connect to Kafka with backoff until broker is ready."""
    for attempt in range(1, max_retries + 1):
        try:
            producer = KafkaProducer(
                bootstrap_servers=[bootstrap],
                key_serializer=lambda k: k.encode("utf-8"),
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                acks="all",
            )
            producer.bootstrap_connected()
            logger.info("Connected to Kafka at %s", bootstrap)
            return producer
        except NoBrokersAvailable:
            if attempt == max_retries:
                raise
            wait = min(delay_sec * attempt, 10)
            logger.warning(
                "Kafka not ready (attempt %s/%s), retrying in %.1fs...",
                attempt,
                max_retries,
                wait,
            )
            time.sleep(wait)

    raise RuntimeError("unreachable")


def run() -> None:
    config = load_producer_config()
    producer = create_producer(config.kafka_bootstrap)
    generator = TickGenerator(config.symbols)

    logger.info(
        "Publishing to topic=%s interval=%ss symbols=%s",
        config.kafka_topic,
        config.tick_interval_sec,
        ",".join(config.symbols),
    )

    try:
        while True:
            tick = generator.next_tick()
            future = producer.send(
                config.kafka_topic,
                key=tick["symbol"],
                value=tick,
            )
            future.get(timeout=10)
            logger.info(
                "published symbol=%s price=%s timestamp=%s",
                tick["symbol"],
                tick["price"],
                tick["timestamp"],
            )
            time.sleep(config.tick_interval_sec)
    except KeyboardInterrupt:
        logger.info("Producer stopped")
    finally:
        producer.flush()
        producer.close()


if __name__ == "__main__":
    try:
        run()
    except NoBrokersAvailable:
        logger.error(
            "Could not connect to Kafka at %s",
            load_producer_config().kafka_bootstrap,
        )
        sys.exit(1)
