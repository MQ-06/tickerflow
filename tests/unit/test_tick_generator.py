from src.common.config import DEFAULT_SYMBOLS
from src.producer.tick_generator import TickGenerator


def test_tick_has_constitution_fields():
    tick = TickGenerator().next_tick()

    assert set(tick.keys()) == {"symbol", "price", "volume", "timestamp", "side"}
    assert tick["symbol"] in DEFAULT_SYMBOLS
    assert tick["price"] > 0
    assert tick["volume"] > 0
    assert tick["timestamp"].endswith("Z")
    assert tick["side"] in ("buy", "sell")


def test_tick_rotates_symbols():
    generator = TickGenerator(DEFAULT_SYMBOLS)
    symbols = {generator.next_tick()["symbol"] for _ in range(len(DEFAULT_SYMBOLS))}
    assert symbols == set(DEFAULT_SYMBOLS)
