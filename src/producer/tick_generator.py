import random
from datetime import datetime, timezone

from src.common.config import DEFAULT_SYMBOLS

# Realistic starting prices per constitution symbol
SEED_PRICES: dict[str, float] = {
    "AAPL": 180.0,
    "MSFT": 420.0,
    "GOOGL": 175.0,
    "TSLA": 245.0,
    "AMZN": 195.0,
}


class TickGenerator:
    """Synthetic tick stream using a simple geometric random walk per symbol."""

    def __init__(self, symbols: tuple[str, ...] = DEFAULT_SYMBOLS) -> None:
        self._symbols = symbols
        self._prices = {
            symbol: SEED_PRICES.get(symbol, 100.0) for symbol in symbols
        }
        self._symbol_index = 0

    def next_tick(self) -> dict:
        symbol = self._symbols[self._symbol_index % len(self._symbols)]
        self._symbol_index += 1

        price = self._prices[symbol]
        price *= 1 + random.gauss(0, 0.001)
        price = round(max(price, 0.01), 2)
        self._prices[symbol] = price

        return {
            "symbol": symbol,
            "price": price,
            "volume": random.randint(100, 10_000),
            "timestamp": datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
            "side": random.choice(("buy", "sell")),
        }
