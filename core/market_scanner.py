from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence

import pandas as pd

from api.kis_client import KisApiError
from .data_fetcher import (
    CHANGE_RATE_COL,
    CLOSE_COL,
    FOREIGN_NET_AMOUNT_COL,
    INSTITUTION_NET_AMOUNT_COL,
    DataFetcher,
    DataNotSufficientError,
)
from .strategy import SectorAnalysisStrategy


ProgressCallback = Callable[[float, str], None]


class MarketScanner:
    """Coordinate stock scanning without owning data loading or strategy logic."""

    def __init__(
        self,
        data_fetcher: DataFetcher,
        strategies: Sequence[SectorAnalysisStrategy],
    ) -> None:
        if data_fetcher is None:
            raise ValueError("data_fetcher must be injected.")
        if not strategies:
            raise ValueError("at least one strategy must be injected.")

        self.data_fetcher = data_fetcher
        self.strategies = list(strategies)

    def run_scan(
        self,
        tickers: Iterable[Dict[str, Any]] | pd.DataFrame,
        max_workers: int = 10,
        progress_callback: Optional[ProgressCallback] = None,
        target_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Scan injected ticker metadata and isolate per-stock failures."""
        ticker_rows = self._normalize_tickers(tickers)
        if not ticker_rows:
            return {"results": pd.DataFrame(), "failures": []}

        results: List[Dict[str, Any]] = []
        failures: List[Dict[str, Any]] = []
        worker_count = max(1, min(max_workers, len(ticker_rows)))

        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            future_to_row = {
                executor.submit(self._process_stock, row, target_date): row for row in ticker_rows
            }
            total = len(future_to_row)
            for completed, future in enumerate(as_completed(future_to_row), start=1):
                output = future.result()
                if output["ok"]:
                    if output["result"] is not None:
                        results.append(output["result"])
                else:
                    failures.append(output["failure"])

                if progress_callback is not None:
                    progress_callback(completed / total, f"{completed}/{total} scanned")

        results_df = pd.DataFrame(results)
        if not results_df.empty and "contribution_score" in results_df.columns:
            results_df = results_df.sort_values(
                by="contribution_score", ascending=False
            ).reset_index(drop=True)

        return {
            "results": results_df,
            "failures": failures,
        }

    def _process_stock(
        self,
        ticker_row: Dict[str, Any],
        target_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        ticker = str(ticker_row.get("code", "")).strip()
        name = ticker_row.get("name", "")

        try:
            if not ticker:
                raise DataNotSufficientError("Ticker code is missing.")

            df = self.data_fetcher.get_and_process_data(ticker, target_date=target_date)
            if "market_cap" not in df.columns:
                df = df.copy()
                df["market_cap"] = ticker_row.get("market_cap", ticker_row.get("cap", 0))

            strategy_results = [strategy.analyze(df) for strategy in self.strategies]
            result = self._build_result(ticker_row, df, strategy_results)
            if not (result.get("is_p1") or result.get("is_p2") or result.get("is_p3")):
                return {
                    "ok": False,
                    "failure": self._build_failure(
                        ticker,
                        name,
                        "ConditionNotMet",
                        "전략 조건 미달 (P1/P2/P3 모두 불합격)",
                    ),
                }

            return {"ok": True, "result": result}

        except (KisApiError, DataNotSufficientError) as exc:
            return {
                "ok": False,
                "failure": self._build_failure(ticker, name, type(exc).__name__, str(exc)),
            }
        except Exception as exc:
            return {
                "ok": False,
                "failure": self._build_failure(ticker, name, type(exc).__name__, str(exc)),
            }

    def _build_result(
        self,
        ticker_row: Dict[str, Any],
        df: pd.DataFrame,
        strategy_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        current = df.iloc[-1]
        p1 = self._find_strategy_result(strategy_results, "P1")
        p2 = self._find_strategy_result(strategy_results, "P2")
        p3 = self._find_strategy_result(strategy_results, "P3")

        return {
            "code": ticker_row.get("code"),
            "name": ticker_row.get("name"),
            "market": ticker_row.get("market"),
            "market_cap": ticker_row.get("market_cap", ticker_row.get("cap", 0)),
            "current_price": current.get(CLOSE_COL),
            "change_rate": current.get(CHANGE_RATE_COL),
            "foreign_net_amount": current.get(FOREIGN_NET_AMOUNT_COL, 0),
            "institution_net_amount": current.get(INSTITUTION_NET_AMOUNT_COL, 0),
            "is_p1": bool(p1.get("is_p1", False)),
            "is_p2": bool(p2.get("is_p2", False)),
            "is_p3": bool(p3.get("is_p3", False)),
            "contribution_score": p1.get("contribution_score", 0.0),
            "p1_result": p1,
            "p2_result": p2,
            "p3_result": p3,
        }

    def _find_strategy_result(
        self, strategy_results: List[Dict[str, Any]], strategy_name: str
    ) -> Dict[str, Any]:
        for result in strategy_results:
            if result.get("strategy") == strategy_name:
                return result
        return {}

    def _build_failure(
        self, ticker: str, name: Any, error_type: str, message: str
    ) -> Dict[str, Any]:
        return {
            "code": ticker,
            "name": name,
            "error_type": error_type,
            "message": message,
        }

    def _normalize_tickers(
        self, tickers: Iterable[Dict[str, Any]] | pd.DataFrame
    ) -> List[Dict[str, Any]]:
        if isinstance(tickers, pd.DataFrame):
            return tickers.to_dict(orient="records")
        return [dict(row) for row in tickers]
