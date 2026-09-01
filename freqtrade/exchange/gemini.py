"""Gemini exchange subclass."""

import logging

from freqtrade.constants import BuySell
from freqtrade.exchange import Exchange
from freqtrade.exchange.exchange_types import FtHas


logger = logging.getLogger(__name__)


class Gemini(Exchange):
    """Gemini exchange class.

    Contains adjustments needed for Freqtrade to work with this exchange.

    Please note that Gemini only supports limit orders natively; market orders
    are not available on this exchange. Configure `order_types` accordingly.
    """

    _ft_has: FtHas = {
        "order_time_in_force": ["GTC", "IOC", "FOK", "PO"],
        # The candles endpoint has no "since" parameter - it always returns the most
        # recent window for the requested timeframe, so history cannot be paginated.
        "ohlcv_has_history": False,
        # Gemini returns a fixed time window per timeframe rather than a fixed count.
        # Values below are the (rounded down) candle counts that window translates to.
        "ohlcv_candle_limit": 360,
        "ohlcv_candle_limit_per_timeframe": {
            "1m": 1440,
            "5m": 2000,
            "15m": 1300,
            "30m": 1400,
            "1h": 1400,
            "6h": 360,
            "1d": 360,
        },
    }

    def _get_params(
        self,
        side: BuySell,
        ordertype: str,
        leverage: float,
        reduceOnly: bool,
        time_in_force: str = "GTC",
    ) -> dict:
        params = super()._get_params(
            side=side,
            ordertype=ordertype,
            leverage=leverage,
            reduceOnly=reduceOnly,
            time_in_force=time_in_force,
        )
        if time_in_force == "PO":
            params.pop("timeInForce", None)
            params["postOnly"] = True
        return params
