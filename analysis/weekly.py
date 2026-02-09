"""Weekly technical analysis calculations."""

from datetime import date, timedelta

import pandas as pd
from data.cache import get_cached_ticker
from indicators.rsi_bb import calculate_rsi, get_rsi_zone
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

    # Ensure we only use complete weekly candles.
    # yfinance dates weekly bars on Monday. On weekdays (Mon-Fri) the
    # current week is still incomplete, so drop it if present.
    last_bar_date = pd.Timestamp(weekly_df.index[-1]).date()
    today = date.today()
    if today.weekday() < 5:  # Mon-Fri: current week may be incomplete
        current_week_monday = today - timedelta(days=today.weekday())
        if last_bar_date >= current_week_monday:
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
            'rsi': None,
            'rsi_zone': 'N/A',
            'ma_distance': 'N/A',
            'trend': 'Insufficient Data',
            'trend_strength': 'N/A',
            'adx': None,
            'tsmom_score': None,
            'tsmom_details': [],
            'tsmom_returns': [],
            'ma_score': None,
            'ma_max': None,
            'ma_details': [],
            'regime': 'UNKNOWN',
            'regime_bias': 'Insufficient data'
        }

    # Calculate indicators on weekly data
    close_weekly = weekly_df['Close']
    rsi = calculate_rsi(close_weekly)
    rsi_zone = get_rsi_zone(rsi)
    ma_distance = format_ma_distance(close_weekly, price, MA_PERIODS)

    if len(weekly_df) >= 50:
        trend, trend_strength, adx = detect_trend(weekly_df, timeframe='weekly')
    else:
        trend, trend_strength, adx = "Insufficient Data", "N/A", None

    # Trend-following indicators
    tsmom_score, tsmom_details, tsmom_returns = calculate_tsmom(close_weekly)
    ma_score, ma_max, ma_details = calculate_ma_score(close_weekly, price)  # Keep for display

    # Regime classification (ADX + TSMOM + RSI)
    regime, regime_bias = classify_regime(adx, tsmom_score, rsi)

    return {
        'price': price,
        'weekly_date': weekly_date,
        'weeks': weeks_available,
        'rsi': rsi,
        'rsi_zone': rsi_zone,
        'ma_distance': ma_distance,
        'trend': trend,
        'trend_strength': trend_strength,
        'adx': adx,
        'tsmom_score': tsmom_score,
        'tsmom_details': tsmom_details,
        'tsmom_returns': tsmom_returns,
        'ma_score': ma_score,      # Display only
        'ma_max': ma_max,          # Display only
        'ma_details': ma_details,  # Display only
        'regime': regime,
        'regime_bias': regime_bias
    }
