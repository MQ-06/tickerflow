import pytest
from pydantic import ValidationError

from src.common.models.tick import Tick


def test_valid_tick():
    tick = Tick.from_dict(
        {
            "symbol": "AAPL",
            "price": 182.34,
            "volume": 500,
            "timestamp": "2026-06-30T10:31:05Z",
            "side": "buy",
        }
    )
    assert tick.symbol == "AAPL"
    assert tick.partition_date() == "2026-06-30"


def test_rejects_negative_price():
    with pytest.raises(ValidationError):
        Tick.from_dict(
            {
                "symbol": "AAPL",
                "price": -1,
                "volume": 100,
                "timestamp": "2026-06-30T12:00:00Z",
                "side": "buy",
            }
        )


def test_rejects_unknown_symbol():
    with pytest.raises(ValidationError):
        Tick.from_dict(
            {
                "symbol": "FAKE",
                "price": 10.0,
                "volume": 100,
                "timestamp": "2026-06-30T12:00:00Z",
                "side": "buy",
            }
        )


def test_rejects_invalid_side():
    with pytest.raises(ValidationError):
        Tick.from_dict(
            {
                "symbol": "TSLA",
                "price": 100.0,
                "volume": 100,
                "timestamp": "2026-06-30T12:00:00Z",
                "side": "hold",
            }
        )
