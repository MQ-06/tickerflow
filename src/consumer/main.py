import json
import logging
import signal
import sys
import time

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from pydantic import ValidationError

from src.common.config import load_consumer_config
from src.common.models.tick import Tick
from src.consumer.writer import LakeWriter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

_shutdown = False


def _handle_signal(signum: int, frame: object) -> None:
    global _shutdown
    logger.info("Shutdown signal received (%s)", signum)
    _shutdown = True


def run() -> None:
    global _shutdown
    config = load_consumer_config()
    writer = LakeWriter(config)

    consumer = KafkaConsumer(
        config.kafka_topic,
        bootstrap_servers=[config.kafka_bootstrap],
        group_id=config.kafka_group_id,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    batch: list[Tick] = []
    last_flush = time.monotonic()
    processed = 0

    logger.info(
        "Consumer started topic=%s group=%s batch_size=%s flush_sec=%s",
        config.kafka_topic,
        config.kafka_group_id,
        config.batch_size,
        config.batch_flush_sec,
    )

    try:
        while not _shutdown:
            records = consumer.poll(timeout_ms=1000)
            for _tp, messages in records.items():
                for message in messages:
                    raw = message.value
                    try:
                        tick = Tick.from_dict(raw)
                        batch.append(tick)
                        processed += 1
                        logger.info(
                            "validated symbol=%s price=%s offset=%s",
                            tick.symbol,
                            tick.price,
                            message.offset,
                        )
                    except ValidationError as exc:
                        errors = [f"{e['loc']}: {e['msg']}" for e in exc.errors()]
                        writer.write_quarantine(raw, errors)
                        consumer.commit()
                        continue

                    if len(batch) >= config.batch_size:
                        writer.write_parquet_batch(batch)
                        batch.clear()
                        consumer.commit()
                        last_flush = time.monotonic()

            if batch and (time.monotonic() - last_flush) >= config.batch_flush_sec:
                writer.write_parquet_batch(batch)
                batch.clear()
                consumer.commit()
                last_flush = time.monotonic()

        if batch:
            writer.write_parquet_batch(batch)
            consumer.commit()
    finally:
        consumer.close()
        logger.info("Consumer stopped after processing %s valid ticks", processed)


if __name__ == "__main__":
    try:
        run()
    except NoBrokersAvailable:
        logger.error("Could not connect to Kafka")
        sys.exit(1)
