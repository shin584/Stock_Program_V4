import pytest

from Stock_Program_V4.core.market_universe import MarketUniverse


def test_market_universe_is_created_with_market_tickers():
    universe = MarketUniverse(
        kospi200_tickers={"005930", "000660"},
        kosdaq150_tickers={"091990", "035900"},
    )

    assert universe.kospi200_tickers == frozenset({"005930", "000660"})
    assert universe.kosdaq150_tickers == frozenset({"091990", "035900"})
    assert universe.get_all_tickers() == frozenset(
        {"005930", "000660", "091990", "035900"}
    )


def test_contains_returns_whether_ticker_exists_in_any_market():
    universe = MarketUniverse(
        kospi200_tickers={"005930"},
        kosdaq150_tickers={"091990"},
    )

    assert universe.contains("005930") is True
    assert universe.contains("091990") is True
    assert universe.contains("373220") is False


def test_market_universe_does_not_expose_mutable_internal_sets():
    universe = MarketUniverse(
        kospi200_tickers={"005930"},
        kosdaq150_tickers={"091990"},
    )

    with pytest.raises(AttributeError):
        universe.kospi200_tickers.add("000660")

    with pytest.raises(AttributeError):
        universe.kosdaq150_tickers.remove("091990")

    with pytest.raises(AttributeError):
        universe.get_all_tickers().add("035900")

    assert universe.contains("000660") is False
    assert universe.contains("091990") is True
