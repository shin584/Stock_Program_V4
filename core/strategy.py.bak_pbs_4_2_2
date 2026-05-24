from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

import pandas as pd

from .data_fetcher import (
    CHANGE_RATE_COL,
    CLOSE_COL,
    FOREIGN_NET_AMOUNT_COL,
    INSTITUTION_NET_AMOUNT_COL,
    TRADE_VALUE_COL,
    VOLUME_COL,
)


ONE_EOK = 100_000_000


class SectorAnalysisStrategy(ABC):
    """Pure strategy interface for stock leadership analysis."""

    @abstractmethod
    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze one stock DataFrame and return a result dictionary."""


class P1Strategy(SectorAnalysisStrategy):
    """Rule 1: classify as P1 when market cap times daily change is positive."""

    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty or CHANGE_RATE_COL not in df.columns or "market_cap" not in df.columns:
            return {"strategy": "P1", "is_p1": False, "contribution_score": 0.0}

        current = df.iloc[-1]
        change_rate = _to_float(current.get(CHANGE_RATE_COL))
        market_cap = _to_float(current.get("market_cap"))
        contribution_score = market_cap * (change_rate / 100)

        return {
            "strategy": "P1",
            "is_p1": contribution_score > 0,
            "contribution_score": contribution_score,
        }


class P2Strategy(SectorAnalysisStrategy):
    """Rule 2: supply-demand leader filter."""

    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        required_columns = {
            CLOSE_COL,
            CHANGE_RATE_COL,
            TRADE_VALUE_COL,
            FOREIGN_NET_AMOUNT_COL,
            INSTITUTION_NET_AMOUNT_COL,
        }
        if df.empty or not required_columns.issubset(df.columns):
            return {"strategy": "P2", "is_p2": False, "failed_rule": "data"}

        current = df.iloc[-1]
        change_rate = _to_float(current.get(CHANGE_RATE_COL))
        if not 1.0 <= change_rate <= 5.0:
            return {"strategy": "P2", "is_p2": False, "failed_rule": "price"}

        trade_value = _to_float(current.get(TRADE_VALUE_COL))
        if trade_value < 150 * ONE_EOK:
            return {"strategy": "P2", "is_p2": False, "failed_rule": "liquidity"}
        if change_rate < 2.0 and trade_value < 500 * ONE_EOK:
            return {"strategy": "P2", "is_p2": False, "failed_rule": "liquidity"}

        disparity = _calculate_ma5_disparity(df)
        if disparity["is_overheated"]:
            return {
                "strategy": "P2",
                "is_p2": False,
                "failed_rule": "disparity",
                "disparity": disparity["value"],
            }

        foreign_buy_days = _count_consecutive_positive(df[FOREIGN_NET_AMOUNT_COL])
        institution_buy_days = _count_consecutive_positive(df[INSTITUTION_NET_AMOUNT_COL])
        trigger_passed = (
            foreign_buy_days >= 3
            or institution_buy_days >= 3
            or (foreign_buy_days >= 1 and institution_buy_days >= 1 and foreign_buy_days + institution_buy_days >= 2)
        )
        if not trigger_passed:
            return {
                "strategy": "P2",
                "is_p2": False,
                "failed_rule": "trigger",
                "foreign_buy_days": foreign_buy_days,
                "institution_buy_days": institution_buy_days,
            }

        recent = df.tail(5)
        accumulated_foreign = _numeric_sum(recent[FOREIGN_NET_AMOUNT_COL])
        accumulated_institution = _numeric_sum(recent[INSTITUTION_NET_AMOUNT_COL])
        today_foreign = _to_float(current.get(FOREIGN_NET_AMOUNT_COL))
        today_institution = _to_float(current.get(INSTITUTION_NET_AMOUNT_COL))
        magnitude_passed = (
            accumulated_foreign >= 100 * ONE_EOK
            or accumulated_institution >= 100 * ONE_EOK
            or today_foreign >= 30 * ONE_EOK
            or today_institution >= 30 * ONE_EOK
        )
        if not magnitude_passed:
            return {"strategy": "P2", "is_p2": False, "failed_rule": "magnitude"}
        
        stage_text = "초기포착" if disparity["value"] <= 10.0 else "추세확정" # V3의 105 기준을 disparity 수치로 변환
        
        if foreign_buy_days > 0 and institution_buy_days > 0:
            reason_text = "쌍끌이"
        elif foreign_buy_days >= 3:
            reason_text = f"외인주도({foreign_buy_days}일)"
        else:
            reason_text = f"기관주도({institution_buy_days}일)"

        return {
            "strategy": "P2",
            "is_p2": True,
            "failed_rule": None,
            "p2_stage": stage_text,
            "p2_reason": reason_text,
            "foreign_buy_days": foreign_buy_days,
            "institution_buy_days": institution_buy_days,
            "accumulated_foreign_5d": accumulated_foreign,
            "accumulated_institution_5d": accumulated_institution,
        }


class P3Strategy(SectorAnalysisStrategy):
    """Rule 3: sniper filter based on price range and volume surge."""

    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty or len(df) < 2 or CHANGE_RATE_COL not in df.columns or VOLUME_COL not in df.columns:
            return {"strategy": "P3", "is_p3": False, "failed_rule": "data"}

        current = df.iloc[-1]
        previous = df.iloc[-2]
        change_rate = _to_float(current.get(CHANGE_RATE_COL))
        if not 0.0 < change_rate <= 5.0:
            return {"strategy": "P3", "is_p3": False, "failed_rule": "price"}

        previous_volume = _to_float(previous.get(VOLUME_COL))
        current_volume = _to_float(current.get(VOLUME_COL))
        if previous_volume <= 0:
            return {"strategy": "P3", "is_p3": False, "failed_rule": "volume"}

        volume_ratio = (current_volume - previous_volume) / previous_volume
        if volume_ratio < 0.5:
            return {
                "strategy": "P3",
                "is_p3": False,
                "failed_rule": "volume",
                "volume_ratio": volume_ratio,
            }

        return {
            "strategy": "P3",
            "is_p3": True,
            "failed_rule": None,
            "volume_ratio": volume_ratio,
            "reason": f"Vol Surge +{volume_ratio * 100:.1f}%"
        }


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _count_consecutive_positive(series: pd.Series) -> int:
    count = 0
    for value in reversed(series.tolist()):
        if _to_float(value) <= 0:
            break
        count += 1
    return count


def _numeric_sum(series: pd.Series) -> float:
    return float(pd.to_numeric(series, errors="coerce").fillna(0).sum())


def _calculate_ma5_disparity(df: pd.DataFrame) -> Dict[str, Any]:
    if "MA5" in df.columns and "MA20" in df.columns:
        ma5 = _to_float(df.iloc[-1].get("MA5"))
        ma20 = _to_float(df.iloc[-1].get("MA20"))
    elif len(df) >= 20:
        close = pd.to_numeric(df[CLOSE_COL], errors="coerce")
        ma5 = float(close.rolling(window=5).mean().iloc[-1])
        ma20 = float(close.rolling(window=20).mean().iloc[-1])
    else:
        return {"is_overheated": False, "value": 0.0}

    close_price = _to_float(df.iloc[-1].get(CLOSE_COL))
    if ma5 <= 0 or ma20 <= 0 or ma5 <= ma20:
        return {"is_overheated": False, "value": 0.0}

    disparity = (close_price - ma5) / ma5 * 100
    return {"is_overheated": disparity > 5.0, "value": disparity}
