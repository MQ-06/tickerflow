import os

from src.common.config import DEFAULT_SYMBOLS, load_producer_config


def test_load_producer_config_defaults(monkeypatch):
    monkeypatch.delenv("KAFKA_BOOTSTRAP", raising=False)
    monkeypatch.delenv("KAFKA_TOPIC", raising=False)
    monkeypatch.delenv("TICK_INTERVAL_SEC", raising=False)
    monkeypatch.delenv("SYMBOLS", raising=False)

    config = load_producer_config()

    assert config.kafka_bootstrap == "localhost:9092"
    assert config.kafka_topic == "stock-ticks"
    assert config.tick_interval_sec == 1.0
    assert config.symbols == DEFAULT_SYMBOLS


def test_load_producer_config_from_env(monkeypatch):
    monkeypatch.setenv("KAFKA_BOOTSTRAP", "kafka:9092")
    monkeypatch.setenv("KAFKA_TOPIC", "ticks")
    monkeypatch.setenv("TICK_INTERVAL_SEC", "0.5")
    monkeypatch.setenv("SYMBOLS", "aapl, tsla")

    config = load_producer_config()

    assert config.kafka_bootstrap == "kafka:9092"
    assert config.kafka_topic == "ticks"
    assert config.tick_interval_sec == 0.5
    assert config.symbols == ("AAPL", "TSLA")
