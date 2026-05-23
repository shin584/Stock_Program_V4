from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TICKERS_FILE = PROJECT_ROOT / "tickers.json"
SCAN_MARKETS = ("KOSPI", "KOSDAQ")


class TickerLoadError(Exception):
    """Raised when ticker metadata cannot be loaded."""


def load_tickers(top_n: int = 100) -> pd.DataFrame:
    """Load top KOSPI and KOSDAQ tickers as one scan-ready DataFrame."""
    if top_n < 1:
        raise TickerLoadError("top_n must be at least 1.")

    data = _read_ticker_data(DEFAULT_TICKERS_FILE)
    tickers = pd.DataFrame(data)
    if tickers.empty:
        return tickers
    if "market" not in tickers.columns:
        raise TickerLoadError("Ticker data must include a 'market' column.")

    market_frames = []
    for market in SCAN_MARKETS:
        market_tickers = tickers[tickers["market"] == market]
        market_frames.append(market_tickers.head(top_n).copy())

    return pd.concat(market_frames, ignore_index=True)


def _read_ticker_data(tickers_path: Path) -> List[Dict[str, Any]]:
    if not tickers_path.exists():
        raise TickerLoadError(f"Ticker file not found: {tickers_path}")

    try:
        with tickers_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        raise TickerLoadError(f"Ticker file contains invalid JSON: {tickers_path}") from exc
    except OSError as exc:
        raise TickerLoadError(f"Unable to read ticker file: {tickers_path}") from exc

    if not isinstance(data, list):
        raise TickerLoadError("Ticker file must contain a JSON array.")
    return data
