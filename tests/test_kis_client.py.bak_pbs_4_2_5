import datetime

import pytest

from Stock_Program_V4.api import kis_client as kis_client_module
from Stock_Program_V4.api.kis_client import KisApiError, KisClient


class FixedDateTime(datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2026, 5, 22, tzinfo=tz)


def _client_without_auth():
    client = object.__new__(KisClient)
    client._token_is_valid = lambda: True
    client.refresh_token = lambda: pytest.fail("refresh_token should not be called")
    return client


def test_fetch_market_data_uses_daily_chart_window_and_keeps_investor_request(monkeypatch):
    monkeypatch.setattr(kis_client_module.datetime, "datetime", FixedDateTime)
    client = _client_without_auth()
    calls = []

    def fake_send_request(method, path, tr_id=None, params=None):
        calls.append({"method": method, "path": path, "tr_id": tr_id, "params": params})
        return {"path": path}

    client._send_request = fake_send_request

    payload = client.fetch_market_data("005930")

    assert payload == {
        "price": {"path": "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"},
        "investor": {"path": "/uapi/domestic-stock/v1/quotations/inquire-investor"},
    }
    assert calls[0] == {
        "method": "GET",
        "path": "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
        "tr_id": "FHKST03010100",
        "params": {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": "005930",
            "FID_INPUT_DATE_1": "20260211",
            "FID_INPUT_DATE_2": "20260522",
            "FID_PERIOD_DIV_CODE": "D",
            "FID_ORG_ADJ_PRC": "0",
        },
    }
    assert calls[1] == {
        "method": "GET",
        "path": "/uapi/domestic-stock/v1/quotations/inquire-investor",
        "tr_id": "FHKST01010900",
        "params": {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": "005930"},
    }


def test_fetch_market_data_wraps_unexpected_chart_error_as_kis_api_error():
    client = _client_without_auth()

    def fail_chart_request(method, path, tr_id=None, params=None):
        raise RuntimeError("chart transport failed")

    client._send_request = fail_chart_request

    with pytest.raises(KisApiError, match="daily item chart"):
        client.fetch_market_data("005930")
