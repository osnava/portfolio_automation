"""Trend detection using ADX and moving averages."""

from ta.trend import ADXIndicator, SMAIndicator
from config import ADX_WEEKLY_WINDOW, ADX_DAILY_WINDOW, ADX_NO_TREND, ADX_TREND_EMERGING, ADX_STRONG_TREND


def detect_trend(df, timeframe='weekly'):
    """
    Detect trend using MAs, ADX, and directional indicators.

    ADX Settings by Timeframe:
        Daily: 14-period
        Weekly: 21-period

    ADX Levels:
        < 20: No trend
        20-25: Trend emerging
        25-40: Trending
        > 40: Strong trend

    Args:
        df: DataFrame with OHLC data
        timeframe: 'daily' or 'weekly' (affects ADX period)

    Returns:
        tuple: (trend_direction, trend_strength, adx_value)
    """
    if len(df) < 50:
        return "Insufficient Data", "N/A", None

    close, high, low = df['Close'], df['High'], df['Low']
    price = close.iloc[-1]

    ma20 = SMAIndicator(close, window=20).sma_indicator().iloc[-1]
    ma50 = SMAIndicator(close, window=50).sma_indicator().iloc[-1]
    ma100 = SMAIndicator(close, window=100).sma_indicator().iloc[-1] if len(close) >= 100 else None
    ma200 = SMAIndicator(close, window=200).sma_indicator().iloc[-1] if len(close) >= 200 else None

    # Use appropriate ADX window based on timeframe
    adx_window = ADX_DAILY_WINDOW if timeframe == 'daily' else ADX_WEEKLY_WINDOW
    adx_ind = ADXIndicator(high, low, close, window=adx_window)
    adx = adx_ind.adx().iloc[-1]
    plus_di, minus_di = adx_ind.adx_pos().iloc[-1], adx_ind.adx_neg().iloc[-1]

    score = sum([
        1 if price > ma20 else -1,
        1 if price > ma50 else -1,
        1 if ma20 > ma50 else -1,
        1 if plus_di > minus_di else -1,
    ])
    if ma100 is not None:
        score += (1 if price > ma100 else -1) + (1 if ma50 > ma100 else -1)
    if ma200 is not None:
        ma_above_200 = ma100 > ma200 if ma100 else ma50 > ma200
        score += (1 if price > ma200 else -1) + (1 if ma_above_200 else -1)

    # ADX interpretation based on new levels
    # < 20: No trend
    # 20-25: Trend emerging
    # 25-40: Trending
    # > 40: Strong trend
    if adx < ADX_NO_TREND:
        return "Sideways/Choppy", "No Trend", round(adx, 1)

    if adx < ADX_TREND_EMERGING:
        strength = "Emerging"
        threshold = 4
    elif adx < ADX_STRONG_TREND:
        strength = "Trending"
        threshold = 3
    else:
        strength = "Strong"
        threshold = 2

    if score >= threshold:
        trend = "Uptrend"
    elif score <= -threshold:
        trend = "Downtrend"
    else:
        trend = "Sideways/Choppy"

    return trend, strength, round(adx, 1)


def get_adx_action(adx_value):
    """
    Get recommended action based on ADX value.

    Args:
        adx_value: ADX indicator value

    Returns:
        str: Recommended action
    """
    if adx_value is None:
        return "N/A"

    if adx_value < ADX_NO_TREND:
        return "Use mean-reversion"
    elif adx_value < ADX_TREND_EMERGING:
        return "Trend emerging"
    elif adx_value < ADX_STRONG_TREND:
        return "Follow trend"
    else:
        return "Strong trend, watch reversal"
