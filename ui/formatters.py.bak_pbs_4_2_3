from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd


def format_won(value: Any) -> str:
    amount = _to_float(value)
    if amount == 0:
        return "0"
    if abs(amount) >= 100_000_000:
        return f"{amount / 100_000_000:,.1f}억"
    return f"{amount:,.0f}원"


def format_percent(value: Any) -> str:
    return f"{_to_float(value):.2f}%"


def format_p1(results: pd.DataFrame) -> pd.DataFrame:
    display = _select_columns(
        results,
        {
            "code": "종목코드",
            "name": "종목명",
            "current_price": "현재가",
            "change_rate": "등락률",
            "contribution_score": "기여점수",
            "foreign_net_amount": "외국인순매수",
            "institution_net_amount": "기관순매수",
        },
    )
    return _format_money_and_percent(
        display,
        money_columns=("현재가", "기여점수", "외국인순매수", "기관순매수"),
    )


def format_p2(results: pd.DataFrame) -> pd.DataFrame:
    display = results.copy()
    display["p2_stage"] = _strategy_text(display, "p2_result", "p2_stage")
    display["p2_reason"] = _strategy_text(display, "p2_result", "p2_reason")
    display = _select_columns(
        display,
        {
            "code": "종목코드",
            "name": "종목명",
            "p2_stage": "단계",
            "p2_reason": "포착사유",
            "current_price": "현재가",
            "change_rate": "등락률",
        },
    )
    return _format_money_and_percent(display, money_columns=("현재가",))


def format_p3(results: pd.DataFrame) -> pd.DataFrame:
    display = results.copy()
    display["p3_reason"] = _strategy_text(display, "p3_result", "reason")
    display = _select_columns(
        display,
        {
            "code": "종목코드",
            "name": "종목명",
            "current_price": "현재가",
            "change_rate": "등락률",
            "p3_reason": "Vol Surge",
            "foreign_net_amount": "외국인순매수",
            "institution_net_amount": "기관순매수",
        },
    )
    return _format_money_and_percent(
        display,
        money_columns=("현재가", "외국인순매수", "기관순매수"),
    )


def format_failures(failures: List[Dict[str, Any]]) -> pd.DataFrame:
    if not failures:
        return pd.DataFrame()
    return pd.DataFrame(failures).rename(
        columns={
            "code": "종목코드",
            "name": "종목명",
            "error_type": "오류 유형",
            "message": "상세 사유",
        }
    )


def _select_columns(results: pd.DataFrame, columns: Dict[str, str]) -> pd.DataFrame:
    if results.empty:
        return pd.DataFrame(columns=list(columns.values()))
    selected = [column for column in columns if column in results.columns]
    return results[selected].rename(columns=columns)


def _format_money_and_percent(
    display: pd.DataFrame, money_columns: tuple[str, ...]
) -> pd.DataFrame:
    for column in money_columns:
        if column in display.columns:
            display[column] = display[column].map(format_won)
    if "등락률" in display.columns:
        display["등락률"] = display["등락률"].map(format_percent)
    return display


def _strategy_text(results: pd.DataFrame, result_column: str, text_key: str) -> pd.Series:
    if result_column not in results.columns:
        return pd.Series([""] * len(results), index=results.index)
    return results[result_column].map(
        lambda value: value.get(text_key, "") if isinstance(value, dict) else ""
    )


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
