from __future__ import annotations

from .krx_authenticator import KRXAuthenticationError, KRXAuthenticator
from .market_universe import MarketUniverse


KOSPI200_INDEX_CODE = "1028"
KOSDAQ150_INDEX_CODE = "2203"
stock = None


class MarketDataFacadeError(Exception):
    """Raised when external market data cannot be fetched."""


class MarketDataFacade:
    """Facade for market data provided by pykrx."""

    def __init__(
        self,
        authenticator: KRXAuthenticator | None = None,
        stock_module: object | None = None,
    ) -> None:
        self._authenticator = authenticator or KRXAuthenticator()
        self._stock_module = stock_module
        self._is_authenticated = False

    def fetch_latest_universe(self) -> MarketUniverse:
        stock_module = self._get_stock_module()

        try:
            kospi200_tickers = stock_module.get_index_portfolio_deposit_file(
                KOSPI200_INDEX_CODE
            )
            kosdaq150_tickers = stock_module.get_index_portfolio_deposit_file(
                KOSDAQ150_INDEX_CODE
            )
        except Exception as exc:
            raise MarketDataFacadeError(
                "Unable to fetch latest market universe from pykrx."
            ) from exc

        return MarketUniverse(
            kospi200_tickers=kospi200_tickers,
            kosdaq150_tickers=kosdaq150_tickers,
        )

    def _get_stock_module(self) -> object:
        self._authenticate_once()

        if self._stock_module is not None:
            return self._stock_module

        if stock is not None:
            self._stock_module = stock
            return self._stock_module

        try:
            from pykrx import stock as pykrx_stock
        except ImportError as exc:
            raise MarketDataFacadeError("pykrx is not installed.") from exc

        self._stock_module = pykrx_stock
        return self._stock_module

    def _authenticate_once(self) -> None:
        if self._is_authenticated:
            return

        try:
            self._authenticator.authenticate()
        except KRXAuthenticationError as exc:
            raise MarketDataFacadeError(str(exc)) from exc

        self._is_authenticated = True
