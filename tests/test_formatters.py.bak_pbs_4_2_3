import pandas as pd

from Stock_Program_V4.ui.formatters import format_p1, format_p2, format_p3


def _result_frame():
    return pd.DataFrame(
        [
            {
                "code": "005930",
                "name": "Alpha",
                "current_price": 100_000,
                "change_rate": 3.25,
                "contribution_score": 12_500_000_000,
                "foreign_net_amount": 3_000_000_000,
                "institution_net_amount": -2_500_000_000,
                "p2_result": {"p2_stage": "초기포착", "p2_reason": "외인주도(3일)"},
                "p3_result": {"reason": "Vol Surge +59.0%"},
            }
        ]
    )


def test_format_p1_uses_index_leader_columns():
    display = format_p1(_result_frame())

    assert list(display.columns) == [
        "종목코드",
        "종목명",
        "현재가",
        "등락률",
        "기여점수",
        "외국인순매수",
        "기관순매수",
    ]
    assert display.iloc[0]["등락률"] == "3.25%"
    assert display.iloc[0]["외국인순매수"] == "30.0억"


def test_format_p2_uses_strategy_text_fields():
    display = format_p2(_result_frame())

    assert list(display.columns) == ["종목코드", "종목명", "단계", "포착사유", "현재가", "등락률"]
    assert display.iloc[0]["단계"] == "초기포착"
    assert display.iloc[0]["포착사유"] == "외인주도(3일)"


def test_format_p3_uses_volume_surge_reason():
    display = format_p3(_result_frame())

    assert list(display.columns) == [
        "종목코드",
        "종목명",
        "현재가",
        "등락률",
        "Vol Surge",
        "외국인순매수",
        "기관순매수",
    ]
    assert display.iloc[0]["Vol Surge"] == "Vol Surge +59.0%"
