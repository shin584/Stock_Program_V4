'''
테스트 항목:

주입된 fake KIS client 사용 시 config 로딩이 호출되지 않는지 검증
get_and_process_data()가 튜플이 아닌 DataFrame만 반환하는지 검증
종가 누락 시 DataNotSufficientError가 발생하는지 검증
실행 결과:

python -m py_compile Stock_Program_V4\core\data_fetcher.py Stock_Program_V4\tests\test_data_fetcher.py
# 통과

python -m pytest Stock_Program_V4\tests\test_data_fetcher.py -q
...                                                                      [100%]
3 passed in 0.98s
'''


import pytest

from Stock_Program_V4.core import data_fetcher as data_fetcher_module
from Stock_Program_V4.core.data_fetcher import (
    CHANGE_RATE_COL,
    CLOSE_COL,
    DATE_COL,
    DataFetcher,
    DataNotSufficientError,
    FOREIGN_NET_AMOUNT_COL,
    INSTITUTION_NET_AMOUNT_COL,
    PERSONAL_NET_AMOUNT_COL,
)


class FakeKisClient:
    def __init__(self, payload):
        self.payload = payload
        self.requested_tickers = []

    def fetch_market_data(self, ticker):
        self.requested_tickers.append(ticker)
        return self.payload


def _sample_payload():
    return {
        "price": {
            "output2": [
                {
                    "stck_bsop_date": "20250101",
                    "stck_clpr": "100",
                    "acml_vol": "10",
                    "acml_tr_pbmn": "1000",
                    "prdy_vrss_sign": "2",
                    "prdy_vrss": "1",
                },
                {
                    "stck_bsop_date": "20250102",
                    "stck_clpr": "110",
                    "acml_vol": "20",
                    "acml_tr_pbmn": "2200",
                    "prdy_vrss_sign": "2",
                    "prdy_vrss": "10",
                },
                {
                    "stck_bsop_date": "20250103",
                    "stck_clpr": "121",
                    "acml_vol": "30",
                    "acml_tr_pbmn": "3630",
                    "prdy_vrss_sign": "2",
                    "prdy_vrss": "11",
                },
                {
                    "stck_bsop_date": "20250104",
                    "stck_clpr": "120",
                    "acml_vol": "40",
                    "acml_tr_pbmn": "4800",
                    "prdy_vrss_sign": "5",
                    "prdy_vrss": "-1",
                },
                {
                    "stck_bsop_date": "20250105",
                    "stck_clpr": "130",
                    "acml_vol": "50",
                    "acml_tr_pbmn": "6500",
                    "prdy_vrss_sign": "2",
                    "prdy_vrss": "10",
                },
            ]
        },
        "investor": {
            "output": [
                {
                    "stck_bsop_date": "20250105",
                    "prsn_ntby_tr_pbmn": "-10",
                    "frgn_ntby_tr_pbmn": "300",
                    "orgn_ntby_tr_pbmn": "200",
                    "prdy_vrss_sign": "2",
                    "prdy_vrss": "10",
                }
            ]
        },
    }


def test_injected_kis_client_is_used_without_loading_config(monkeypatch):
    def fail_if_called():
        raise AssertionError("get_kis_config should not be called when kis_client is injected")

    monkeypatch.setattr(data_fetcher_module, "get_kis_config", fail_if_called)

    fake_client = FakeKisClient(_sample_payload())
    fetcher = DataFetcher(kis_client=fake_client)

    df = fetcher.get_and_process_data(" 005930 ")

    assert fake_client.requested_tickers == ["005930"]
    assert CLOSE_COL in df.columns
    assert {"MA5", "MA20", "MA60", "MACD", "Signal", "MACD_Oscillator"}.issubset(df.columns)


def test_get_and_process_data_returns_dataframe_only():
    fetcher = DataFetcher(kis_client=FakeKisClient(_sample_payload()))

    result = fetcher.get_and_process_data("005930")

    assert not isinstance(result, tuple)
    assert len(result) == 5
    assert result.iloc[-1][CLOSE_COL] == 130
    assert result.index.name == DATE_COL
    assert result.index.is_monotonic_increasing
    assert result.iloc[0][CHANGE_RATE_COL] == 0
    assert result.iloc[1][CHANGE_RATE_COL] == pytest.approx(10.0)
    assert result.iloc[-2][FOREIGN_NET_AMOUNT_COL] == 0
    assert result.iloc[-1][PERSONAL_NET_AMOUNT_COL] == -10_000_000
    assert result.iloc[-1][FOREIGN_NET_AMOUNT_COL] == 300_000_000
    assert result.iloc[-1][INSTITUTION_NET_AMOUNT_COL] == 200_000_000
    assert "prdy_vrss_sign" not in result.columns
    assert "prdy_vrss" not in result.columns


def test_build_price_frame_sorts_daily_chart_rows_by_trading_date():
    fetcher = DataFetcher(kis_client=FakeKisClient({}))

    price_df = fetcher._build_price_frame(
        {
            "output2": [
                {"stck_bsop_date": "20250103", "stck_clpr": "121"},
                {"stck_bsop_date": "20250101", "stck_clpr": "100"},
                {"stck_bsop_date": "20250102", "stck_clpr": "110"},
            ]
        }
    )

    assert price_df.index.name == DATE_COL
    assert list(price_df[CLOSE_COL]) == [100, 110, 121]
    assert list(price_df[CHANGE_RATE_COL]) == pytest.approx([0.0, 10.0, 10.0])


def test_indicator_calculation_raises_when_close_is_missing():
    fetcher = DataFetcher(kis_client=FakeKisClient({"price": {"output2": [{"acml_vol": "10"}]}}))

    with pytest.raises(DataNotSufficientError):
        fetcher.get_and_process_data("005930")
