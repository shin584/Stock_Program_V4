from unittest.mock import Mock

from Stock_Program_V4.core.market_universe import MarketUniverse
from Stock_Program_V4.core.universe_state_manager import UniverseStateManager


def test_get_universe_fetches_once_and_returns_cached_universe():
    universe = MarketUniverse(
        kospi200_tickers={"005930", "000660"},
        kosdaq150_tickers={"091990", "035900"},
    )
    facade = Mock()
    facade.fetch_latest_universe.return_value = universe
    manager = UniverseStateManager(market_data_facade=facade)

    first = manager.get_universe()
    second = manager.get_universe()
    third = manager.get_universe()

    assert first is universe
    assert second is universe
    assert third is universe
    assert facade.fetch_latest_universe.call_count == 1


def test_refresh_universe_clears_cache_and_fetches_latest_universe():
    old_universe = MarketUniverse(
        kospi200_tickers={"005930"},
        kosdaq150_tickers={"091990"},
    )
    new_universe = MarketUniverse(
        kospi200_tickers={"000660"},
        kosdaq150_tickers={"035900"},
    )
    facade = Mock()
    facade.fetch_latest_universe.side_effect = [old_universe, new_universe]
    manager = UniverseStateManager(market_data_facade=facade)

    assert manager.get_universe() is old_universe
    assert manager.refresh_universe() is new_universe
    assert manager.get_universe() is new_universe
    assert facade.fetch_latest_universe.call_count == 2
