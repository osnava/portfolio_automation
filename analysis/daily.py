"""Daily technical analysis calculations."""

import pandas as pd
from ta.trend import ADXIndicator
from data.cache import get_cached_ticker
from indicators.ztanh import calculate_ztanh, get_ztanh_zone
from indicators.momentum import calculate_ma_score, format_ma_distance
from config import ADX_DAILY_WINDOW, ADX_NO_TREND, ADX_TREND_EMERGING, ADX_STRONG_TREND, MA_PERIODS


def calculate_daily_technicals(ticker):
    """
    Calculate daily (1d) technical indicators.

    Indicators:
        - ZTanh: Learned z-score transformation with tanh activation [-1, +1]
        - MA Score: 7-point moving average alignment (20/50/100/200)
        - MA Distance: Percentage distance from each MA
        - ADX: 14-period Average Directional Index with trend classification
    """
    # Fetch 1 year of daily data (always fresh - daily prices are critical for entry timing)
    data = get_cached_ticker(ticker, period="1y", interval="1d", fresh=True)

    if data.empty or len(data) < 200:
        return None

    close = data['Close']
    high = data['High']
    low = data['Low']
    price = close.iloc[-1]
    daily_date = pd.Timestamp(data.index[-1]).strftime('%Y-%m-%d')

    # Daily ZTanh (using ticker-specific weights)
    ztanh_daily = calculate_ztanh(close, ticker=ticker)
    ztanh_zone_daily = get_ztanh_zone(ztanh_daily, ticker=ticker, timeframe='daily')

    # MA Score and Distance
    ma_score, ma_max, ma_details = calculate_ma_score(close, price)
    ma_distance = format_ma_distance(close, price, MA_PERIODS)

    # Daily ADX (14-period)
    adx_ind = ADXIndicator(high, low, close, window=ADX_DAILY_WINDOW)
    adx_daily = adx_ind.adx().iloc[-1]
    plus_di_daily = adx_ind.adx_pos().iloc[-1]
    minus_di_daily = adx_ind.adx_neg().iloc[-1]

    # ADX interpretation
    if adx_daily < ADX_NO_TREND:
        adx_interpretation = "No Trend"
    elif adx_daily < ADX_TREND_EMERGING:
        adx_interpretation = "Emerging"
    elif adx_daily < ADX_STRONG_TREND:
        adx_interpretation = "Trending"
    else:
        adx_interpretation = "Strong"

    # Determine ADX action recommendation
    if adx_daily < ADX_NO_TREND:
        adx_action = "Use ZTanh mean-reversion"
    elif adx_daily > ADX_TREND_EMERGING:
        adx_action = "Follow trend"
    else:
        adx_action = "Trend emerging"

    # Determine directional bias from DI
    if plus_di_daily > minus_di_daily:
        di_bias = "Bullish"
    elif minus_di_daily > plus_di_daily:
        di_bias = "Bearish"
    else:
        di_bias = "Neutral"

    # Daily trend classification based on MA alignment and ADX
    if ma_score >= 6 and adx_daily > ADX_TREND_EMERGING and plus_di_daily > minus_di_daily:
        trend_daily = "Strong Bullish"
    elif ma_score >= 5 and plus_di_daily > minus_di_daily:
        trend_daily = "Bullish"
    elif ma_score <= 1 and adx_daily > ADX_TREND_EMERGING and minus_di_daily > plus_di_daily:
        trend_daily = "Strong Bearish"
    elif ma_score <= 2 and minus_di_daily > plus_di_daily:
        trend_daily = "Bearish"
    else:
        trend_daily = "Mixed"

    return {
        'price': price,
        'daily_date': daily_date,
        'ztanh_daily': ztanh_daily,
        'ztanh_zone_daily': ztanh_zone_daily,
        'ma_score': ma_score,
        'ma_max': ma_max,
        'ma_distance': ma_distance,
        'adx_daily': round(adx_daily, 1),
        'adx_interpretation': adx_interpretation,
        'adx_action': adx_action,
        'plus_di_daily': round(plus_di_daily, 1),
        'minus_di_daily': round(minus_di_daily, 1),
        'di_bias': di_bias,
        'trend_daily': trend_daily,
    }
