"""Weekly technical analysis calculations."""

import pandas as pd
from data.cache import get_cached_ticker
from indicators.ztanh import calculate_ztanh, get_ztanh_zone
from indicators.momentum import calculate_tsmom, calculate_ma_score, format_ma_distance
from indicators.trend import detect_trend
from analysis.regime import classify_regime
from config import MA_PERIODS


def calculate_technicals(ticker):
    """Calculate technical indicators using weekly timeframe only."""
    # Download weekly data directly (complete weeks only)
    # Need ~260 weeks for MA200 weekly (5 years)
    weekly_df = get_cached_ticker(ticker, period="5y", interval="1wk")

    if weekly_df.empty or len(weekly_df) < 50:
        # Fallback: try shorter period
        weekly_df = get_cached_ticker(ticker, period="2y", interval="1wk")

    if weekly_df.empty:
        return None

    # Ensure we only use complete weekly candles (ending Sunday)
    # If last bar is not Sunday (weekday 6), drop it (incomplete week)
    last_bar_date = pd.Timestamp(weekly_df.index[-1])
    if last_bar_date.weekday() != 6:  # Not Sunday
        weekly_df = weekly_df[:-1]
        if weekly_df.empty:
            return None

    # Get price from last COMPLETE weekly candle close
    price = weekly_df['Close'].iloc[-1]
    weekly_date = pd.Timestamp(weekly_df.index[-1]).strftime('%Y-%m-%d')  # Store last complete week date

    weeks_available = len(weekly_df)

    if weeks_available < 26:
        return {
            'price': price,
            'weekly_date': weekly_date,
            'weeks': weeks_available,
            'ztanh': None,
            'ztanh_zone': 'N/A',
            'ma_distance': 'N/A',
            'trend': 'Insufficient Data',
            'trend_strength': 'N/A',
            'adx': None,
            'tsmom_score': None,
            'tsmom_details': [],
            'ma_score': None,
            'ma_max': None,
            'ma_details': [],
            'regime': 'UNKNOWN',
            'regime_bias': 'Insufficient data'
        }

    # Calculate indicators on weekly data (using ticker-specific weights)
    close_weekly = weekly_df['Close']
    ztanh = calculate_ztanh(close_weekly, ticker=ticker)
    ztanh_zone = get_ztanh_zone(ztanh, ticker=ticker, timeframe='weekly')
    ma_distance = format_ma_distance(close_weekly, price, MA_PERIODS)

    if len(weekly_df) >= 50:
        trend, trend_strength, adx = detect_trend(weekly_df, timeframe='weekly')
    else:
        trend, trend_strength, adx = "Insufficient Data", "N/A", None

    # Trend-following indicators
    tsmom_score, tsmom_details = calculate_tsmom(close_weekly)
    ma_score, ma_max, ma_details = calculate_ma_score(close_weekly, price)

    # Regime classification (uses ticker-specific ztanh thresholds)
    regime, regime_bias = classify_regime(adx, tsmom_score, ztanh, ma_score, ma_max, ticker=ticker)

    return {
        'price': price,
        'weekly_date': weekly_date,
        'weeks': weeks_available,
        'ztanh': ztanh,
        'ztanh_zone': ztanh_zone,
        'ma_distance': ma_distance,
        'trend': trend,
        'trend_strength': trend_strength,
        'adx': adx,
        'tsmom_score': tsmom_score,
        'tsmom_details': tsmom_details,
        'ma_score': ma_score,
        'ma_max': ma_max,
        'ma_details': ma_details,
        'regime': regime,
        'regime_bias': regime_bias
    }
