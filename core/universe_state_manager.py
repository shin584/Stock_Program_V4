from __future__ import annotations

from .market_data_facade import MarketDataFacade
from .market_universe import MarketUniverse


class UniverseStateManager:
    """Manage the in-memory lifecycle of the target market universe."""

    def __init__(self, market_data_facade: MarketDataFacade | None = None) -> None:
        self._market_data_facade = market_data_facade or MarketDataFacade()
        self._cached_universe: MarketUniverse | None = None

    def get_universe(self) -> MarketUniverse:
        if self._cached_universe is None:
            self._cached_universe = self._market_data_facade.fetch_latest_universe()
        return self._cached_universe

    def refresh_universe(self) -> MarketUniverse:
        self._cached_universe = None
        return self.get_universe()
