"""Daily technical analysis calculations."""

import pandas as pd
from ta.trend import ADXIndicator
from data.cache import get_cached_ticker
from indicators.zscore import calculate_zscore
from indicators.tema import calculate_tema, calculate_tema_ensemble, detect_cross


def calculate_daily_technicals(ticker):
    """Calculate daily (1d) technical indicators using TEMA crosses."""
    # Fetch 1 year of daily data
    data = get_cached_ticker(ticker, period="1y", interval="1d")

    if data.empty or len(data) < 200:
        return None

    close = data['Close']
    high = data['High']
    low = data['Low']
    price = close.iloc[-1]
    daily_date = pd.Timestamp(data.index[-1]).strftime('%Y-%m-%d')  # Store last daily candle date

    # Daily Z-score (20-day window)
    zscore_daily, zone_daily = calculate_zscore(close, window=20)

    # Calculate TEMA for 20, 50, 200 periods
    tema20 = calculate_tema(close, 20)
    tema50 = calculate_tema(close, 50)
    tema200 = calculate_tema(close, 200)

    # Current and previous values for cross detection
    tema20_curr = tema20.iloc[-1]
    tema20_prev = tema20.iloc[-2]
    tema50_curr = tema50.iloc[-1]
    tema50_prev = tema50.iloc[-2]
    tema200_curr = tema200.iloc[-1]
    tema200_prev = tema200.iloc[-2]

    # Detect crosses
    cross_20_50 = detect_cross(tema20_curr, tema20_prev, tema50_curr, tema50_prev)
    cross_50_200 = detect_cross(tema50_curr, tema50_prev, tema200_curr, tema200_prev)

    # TEMA alignment (similar to MA score but with TEMA)
    tema_alignment = 0
    if tema20_curr > tema50_curr:
        tema_alignment += 1
    if tema50_curr > tema200_curr:
        tema_alignment += 1
    if price > tema20_curr:
        tema_alignment += 1

    # Daily ADX
    adx_ind = ADXIndicator(high, low, close, window=14)
    adx_daily = adx_ind.adx().iloc[-1]
    plus_di_daily = adx_ind.adx_pos().iloc[-1]
    minus_di_daily = adx_ind.adx_neg().iloc[-1]

    # Daily trend classification
    if tema20_curr > tema50_curr > tema200_curr and price > tema20_curr:
        trend_daily = "Strong Bullish"
    elif tema20_curr > tema50_curr and price > tema20_curr:
        trend_daily = "Bullish"
    elif tema20_curr < tema50_curr < tema200_curr and price < tema20_curr:
        trend_daily = "Strong Bearish"
    elif tema20_curr < tema50_curr and price < tema20_curr:
        trend_daily = "Bearish"
    else:
        trend_daily = "Mixed"

    # Distance from TEMAs (%)
    tema20_dist = ((price - tema20_curr) / tema20_curr) * 100
    tema50_dist = ((price - tema50_curr) / tema50_curr) * 100
    tema200_dist = ((price - tema200_curr) / tema200_curr) * 100

    # Multi-period TEMA ensemble with volatility adjustment
    consensus, confidence, ensemble_str, ensemble_detail, vol_scalar = calculate_tema_ensemble(close, price)

    # Enhanced trend classification using ensemble
    if confidence >= 0.67:  # At least 2/3 periods agree
        if consensus > 0:
            trend_ensemble = "Strong Bullish" if confidence == 1.0 else "Bullish"
        elif consensus < 0:
            trend_ensemble = "Strong Bearish" if confidence == 1.0 else "Bearish"
        else:
            trend_ensemble = "Mixed"
    else:
        trend_ensemble = "Low Confidence"

    return {
        'price': price,
        'daily_date': daily_date,
        'zscore_daily': zscore_daily,
        'zscore_zone_daily': zone_daily,
        'tema20': round(tema20_curr, 2),
        'tema50': round(tema50_curr, 2),
        'tema200': round(tema200_curr, 2),
        'tema20_dist': round(tema20_dist, 2),
        'tema50_dist': round(tema50_dist, 2),
        'tema200_dist': round(tema200_dist, 2),
        'cross_20_50': cross_20_50,
        'cross_50_200': cross_50_200,
        'tema_alignment': f"{tema_alignment}/3",
        'adx_daily': round(adx_daily, 1),
        'plus_di_daily': round(plus_di_daily, 1),
        'minus_di_daily': round(minus_di_daily, 1),
        'trend_daily': trend_daily,
        # NEW: Ensemble metrics
        'tema_consensus': consensus,
        'tema_confidence': confidence,
        'tema_ensemble': ensemble_str,
        'trend_ensemble': trend_ensemble,
        'vol_scalar': vol_scalar,
    }
