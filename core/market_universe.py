from __future__ import annotations

from collections.abc import Iterable


class MarketUniverse:
    """Immutable value object for KOSPI 200 and KOSDAQ 150 ticker sets."""

    def __init__(
        self,
        kospi200_tickers: Iterable[str],
        kosdaq150_tickers: Iterable[str],
    ) -> None:
        self._kospi200_tickers = set(kospi200_tickers)
        self._kosdaq150_tickers = set(kosdaq150_tickers)

    @property
    def kospi200_tickers(self) -> frozenset[str]:
        return frozenset(self._kospi200_tickers)

    @property
    def kosdaq150_tickers(self) -> frozenset[str]:
        return frozenset(self._kosdaq150_tickers)

    def get_all_tickers(self) -> frozenset[str]:
        return frozenset(self._kospi200_tickers | self._kosdaq150_tickers)

    def contains(self, ticker: str) -> bool:
        return ticker in self._kospi200_tickers or ticker in self._kosdaq150_tickers
