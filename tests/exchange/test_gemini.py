from freqtrade.enums import CandleType, MarginMode, TradingMode
from freqtrade.exchange.gemini import Gemini
from tests.conftest import get_patched_exchange


def test_gemini_ft_has(default_conf, mocker):
    exchange = get_patched_exchange(mocker, default_conf, exchange="gemini")

    assert exchange._ft_has["order_time_in_force"] == ["GTC", "IOC", "FOK", "PO"]
    # Gemini's candles endpoint ignores "since" - no history pagination.
    assert exchange._ft_has["ohlcv_has_history"] is False
    assert "supports_demo_trading" not in exchange._ft_has


def test_gemini_ohlcv_candle_limit(default_conf, mocker):
    exchange = get_patched_exchange(mocker, default_conf, exchange="gemini")

    # Gemini returns a fixed time window per timeframe, so the limit varies.
    assert exchange.ohlcv_candle_limit("1m", CandleType.SPOT) == 1440
    assert exchange.ohlcv_candle_limit("1h", CandleType.SPOT) == 1400
    assert exchange.ohlcv_candle_limit("1d", CandleType.SPOT) == 360
    # Timeframes Gemini doesn't serve fall back to the conservative default.
    assert exchange.ohlcv_candle_limit("4h", CandleType.SPOT) == 360


def test_gemini_spot_only():
    # Assert on the class - get_patched_exchange() patches this attribute for tests.
    assert Gemini._supported_trading_mode_margin_pairs == [(TradingMode.SPOT, MarginMode.NONE)]


def test_gemini_get_params_post_only(default_conf, mocker):
    exchange = get_patched_exchange(mocker, default_conf, exchange="gemini")

    params = exchange._get_params(
        side="buy", ordertype="limit", leverage=1.0, reduceOnly=False, time_in_force="PO"
    )
    assert params["postOnly"] is True
    assert "timeInForce" not in params

    params = exchange._get_params(
        side="buy", ordertype="limit", leverage=1.0, reduceOnly=False, time_in_force="IOC"
    )
    assert params["timeInForce"] == "IOC"
    assert "postOnly" not in params
