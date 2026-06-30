import os
from dataclasses import dataclass
from pydantic import BaseModel, Field, field_validator

from src.common.config import DEFAULT_SYMBOLS

VALID_SYMBOLS = set(DEFAULT_SYMBOLS)
VALID_SIDES = {"buy", "sell"}


class Tick(BaseModel):
    symbol: str
    price: float = Field(gt=0)
    volume: int = Field(gt=0)
    timestamp: str
    side: str

    @field_validator("symbol")
    @classmethod
    def symbol_must_be_known(cls, value: str) -> str:
        upper = value.strip().upper()
        if upper not in VALID_SYMBOLS:
            raise ValueError(f"unknown symbol: {value}")
        return upper

    @field_validator("side")
    @classmethod
    def side_must_be_buy_or_sell(cls, value: str) -> str:
        lower = value.strip().lower()
        if lower not in VALID_SIDES:
            raise ValueError(f"side must be buy or sell, got: {value}")
        return lower

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_be_iso(cls, value: str) -> str:
        if not value or "T" not in value:
            raise ValueError("timestamp must be ISO 8601")
        return value

    def partition_date(self) -> str:
        return self.timestamp[:10]

    def to_parquet_row(self) -> dict[str, object]:
        return {
            "symbol": self.symbol,
            "price": self.price,
            "volume": self.volume,
            "timestamp": self.timestamp,
            "side": self.side,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Tick":
        return cls.model_validate(data)
