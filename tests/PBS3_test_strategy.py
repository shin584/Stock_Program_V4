import pandas as pd

from Stock_Program_V4.core.data_fetcher import (
    CHANGE_RATE_COL,
    CLOSE_COL,
    FOREIGN_NET_AMOUNT_COL,
    INSTITUTION_NET_AMOUNT_COL,
    TRADE_VALUE_COL,
    VOLUME_COL,
)
from Stock_Program_V4.core.strategy import P1Strategy, P2Strategy, P3Strategy


def _base_frame(rows=20):
    closes = [100 + i for i in range(rows)]
    return pd.DataFrame(
        {
            CLOSE_COL: closes,
            CHANGE_RATE_COL: [1.5] * rows,
            TRADE_VALUE_COL: [200 * 100_000_000] * rows,
            VOLUME_COL: [1_000] * rows,
            FOREIGN_NET_AMOUNT_COL: [0] * rows,
            INSTITUTION_NET_AMOUNT_COL: [0] * rows,
            "market_cap": [1_000_000_000_000] * rows,
        }
    )


def test_p1_returns_true_when_contribution_score_is_positive():
    df = _base_frame()
    df.loc[df.index[-1], CHANGE_RATE_COL] = 2.0
    df.loc[df.index[-1], "market_cap"] = 1_000_000_000

    result = P1Strategy().analyze(df)

    assert result["is_p1"] is True
    assert result["contribution_score"] == 20_000_000


def test_p1_returns_false_when_contribution_score_is_not_positive():
    df = _base_frame()
    df.loc[df.index[-1], CHANGE_RATE_COL] = -1.0

    result = P1Strategy().analyze(df)

    assert result["is_p1"] is False


def test_p2_returns_true_when_supply_demand_rule_passes():
    df = _base_frame()
    df.loc[df.index[-1], CHANGE_RATE_COL] = 3.0
    df[INSTITUTION_NET_AMOUNT_COL] = [0] * 17 + [40 * 100_000_000] * 3

    result = P2Strategy().analyze(df)

    assert result["is_p2"] is True
    assert result["institution_buy_days"] == 3


def test_p2_returns_false_when_price_rule_fails():
    df = _base_frame()
    df.loc[df.index[-1], CHANGE_RATE_COL] = 6.0
    df[INSTITUTION_NET_AMOUNT_COL] = [0] * 17 + [40 * 100_000_000] * 3

    result = P2Strategy().analyze(df)

    assert result["is_p2"] is False
    assert result["failed_rule"] == "price"


def test_p3_returns_true_when_price_and_volume_surge_pass():
    df = _base_frame(rows=5)
    df.loc[df.index[-2], VOLUME_COL] = 1_000
    df.loc[df.index[-1], VOLUME_COL] = 1_600
    df.loc[df.index[-1], CHANGE_RATE_COL] = 4.5

    result = P3Strategy().analyze(df)

    assert result["is_p3"] is True
    assert result["volume_ratio"] == 0.6


def test_p3_returns_false_when_volume_surge_fails():
    df = _base_frame(rows=5)
    df.loc[df.index[-2], VOLUME_COL] = 1_000
    df.loc[df.index[-1], VOLUME_COL] = 1_400
    df.loc[df.index[-1], CHANGE_RATE_COL] = 4.5

    result = P3Strategy().analyze(df)

    assert result["is_p3"] is False
    assert result["failed_rule"] == "volume"

'''
테스트 결과:

python -m py_compile Stock_Program_V4\core\strategy.py Stock_Program_V4\tests\test_strategy.py
# 통과

python -m pytest Stock_Program_V4\tests\test_strategy.py -q
......                                                                   [100%]
6 passed in 1.19s

python -m pytest Stock_Program_V4\tests -q
.........                                                                [100%]
9 passed in 1.27s
'''
