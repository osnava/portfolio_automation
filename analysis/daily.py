"""Daily technical analysis calculations."""

import pandas as pd
from ta.trend import ADXIndicator
from ta.momentum import KAMAIndicator
from data.cache import get_cached_ticker
from indicators.ztanh import calculate_ztanh, get_ztanh_zone
from config import ADX_DAILY_WINDOW, ADX_NO_TREND, ADX_TREND_EMERGING, ADX_STRONG_TREND
from config import KAMA_WINDOW, KAMA_FAST, KAMA_SLOW_DAILY


def calculate_daily_technicals(ticker):
    """
    Calculate daily (1d) technical indicators.

    Indicators:
        - ZTanh: Learned z-score transformation with tanh activation [-1, +1]
        - ADX: 14-period Average Directional Index with trend classification
        - DI_Bias: Directional indicator bias (+DI vs -DI)
        - KAMA: Kaufman's Adaptive Moving Average (10/2/30) as trend filter
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

    # Daily ADX (14-period)
    adx_ind = ADXIndicator(high, low, close, window=ADX_DAILY_WINDOW)
    adx_daily = adx_ind.adx().iloc[-1]
    plus_di_daily = adx_ind.adx_pos().iloc[-1]
    minus_di_daily = adx_ind.adx_neg().iloc[-1]

    # ADX action recommendation
    if adx_daily < ADX_NO_TREND:
        adx_action = "Mean-reversion"
    elif adx_daily > ADX_TREND_EMERGING:
        adx_action = "Trend-follow"
    else:
        adx_action = "Emerging"

    # Directional bias from DI
    if plus_di_daily > minus_di_daily:
        di_bias = "Bullish"
    elif minus_di_daily > plus_di_daily:
        di_bias = "Bearish"
    else:
        di_bias = "Neutral"

    # KAMA - Kaufman's Adaptive Moving Average (trend filter)
    # Standard params: window=10 (ER period), pow1=2 (fast), pow2=30 (slow)
    kama_ind = KAMAIndicator(close, window=KAMA_WINDOW, pow1=KAMA_FAST, pow2=KAMA_SLOW_DAILY)
    kama = kama_ind.kama().iloc[-1]

    # KAMA distance (percentage)
    kama_dist = ((price - kama) / kama) * 100

    # Price vs KAMA classification
    if kama_dist > 2.0:
        price_vs_kama = "Extended Above"
    elif kama_dist > 0:
        price_vs_kama = "Above"
    elif kama_dist > -2.0:
        price_vs_kama = "Below"
    else:
        price_vs_kama = "Extended Below"

    return {
        'price': price,
        'daily_date': daily_date,
        'ztanh_daily': ztanh_daily,
        'ztanh_zone_daily': ztanh_zone_daily,
        'adx_daily': round(adx_daily, 1),
        'adx_action': adx_action,
        'di_bias': di_bias,
        'kama': round(kama, 4),
        'kama_dist': round(kama_dist, 2),
        'price_vs_kama': price_vs_kama,
    }
