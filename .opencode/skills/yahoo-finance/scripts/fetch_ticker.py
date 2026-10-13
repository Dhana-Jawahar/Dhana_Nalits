#!/usr/bin/env python3
"""Fetch Yahoo Finance snapshot for a ticker via yfinance."""
from __future__ import annotations
import json
import sys
from datetime import datetime, timezone
try:
    import yfinance as yf
except ImportError:
    print("Use a venv: python3 -m venv .venv && .venv/bin/pip install yfinance", file=sys.stderr)
    sys.exit(1)
def normalize(symbol: str) -> str:
    return symbol.strip().upper()
def fetch(symbol: str) -> dict:
    info = yf.Ticker(symbol).info or {}
    def g(*keys, default=None):
        for k in keys:
            if info.get(k) is not None:
                return info[k]
        return default
    return {
        "ticker": symbol,
        "name": g("shortName", "longName", default=symbol),
        "price": g("currentPrice", "regularMarketPrice"),
        "currency": g("currency", default="USD"),
        "shares_outstanding": g("sharesOutstanding"),
        "market_cap": g("marketCap"),
        "trailing_pe": g("trailingPE"),
        "volume": g("volume", "regularMarketVolume"),
        "fifty_two_week_low": g("fiftyTwoWeekLow"),
        "fifty_two_week_high": g("fiftyTwoWeekHigh"),
        "sector": g("sector"),
        "industry": g("industry"),
        "as_of": datetime.now(timezone.utc).isoformat(),
    }
def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: fetch_ticker.py TICKER", file=sys.stderr)
        return 2
    data = fetch(normalize(sys.argv[1]))
    if data.get("price") is None and data.get("market_cap") is None:
        print(json.dumps({"error": f"No data for {data['ticker']}", **data}, indent=2))
        return 1
    print(json.dumps(data, indent=2, default=str))
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
