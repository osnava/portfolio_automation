"""ZTanh indicator - learned z-score transformation with tanh activation."""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from ta.trend import SMAIndicator

# Paths
WEIGHTS_PATH = Path(__file__).parent.parent / "weights.json"
THRESHOLDS_PATH = Path(__file__).parent.parent / "thresholds.json"


def load_weights():
    """Load encoder weights from weights.json."""
    with open(WEIGHTS_PATH, 'r') as f:
        return json.load(f)


def load_thresholds():
    """Load thresholds from thresholds.json."""
    with open(THRESHOLDS_PATH, 'r') as f:
        return json.load(f)


def get_ticker_thresholds(ticker: str, timeframe: str = 'daily'):
    """
    Get thresholds for a specific ticker and timeframe.

    Args:
        ticker: Ticker symbol (e.g., '^VIX', 'BTC-USD', 'SPY')
        timeframe: 'daily' or 'weekly'

    Returns:
        dict: Thresholds for the ticker
    """
    thresholds = load_thresholds()

    # Check if ticker has specific thresholds, otherwise use default
    if ticker in thresholds:
        return thresholds[ticker].get(timeframe, thresholds['default'][timeframe])
    else:
        return thresholds['default'][timeframe]


def get_ticker_weights(ticker: str):
    """
    Get encoder weights for a specific ticker.

    Args:
        ticker: Ticker symbol (e.g., 'SPY', 'BTC-USD', '^VIX')

    Returns:
        dict: Weights with 'encoder_weight' and 'encoder_bias'
    """
    weights = load_weights()

    # Check if ticker has specific weights, otherwise use default
    if ticker in weights:
        return weights[ticker]
    else:
        return weights['default']


def calculate_ztanh(close: pd.Series, ticker: str = 'default', periods: list = [20, 50, 100, 200]) -> float:
    """
    Compute ZTanh signal from close prices using ticker-specific encoder weights.

    The ZTanh indicator combines multiple z-scores across different lookback
    periods using learned weights, then applies tanh activation to bound
    the output to [-1, +1].

    Args:
        close: Price series (pd.Series)
        ticker: Ticker symbol for weight lookup (e.g., 'SPY', 'BTC-USD')
        periods: List of lookback periods for z-score calculation

    Returns:
        ZTanh signal value (float) bounded to [-1, +1]
        Returns None if insufficient data
    """
    # Need enough data for the longest period
    min_required = max(periods) + 10
    if len(close) < min_required:
        return None

    # Get ticker-specific weights
    ticker_weights = get_ticker_weights(ticker)

    # Calculate z-scores for each period
    zscores = {}
    for n in periods:
        ma = SMAIndicator(close, window=n).sma_indicator()
        std = close.rolling(n).std()  # ta doesn't have std indicator
        # Avoid division by zero
        std = std.replace(0, np.nan)
        zscores[f'Z_{n}'] = (close - ma) / std

    # Get the latest values for each z-score
    z_values = []
    for n in periods:
        z_val = zscores[f'Z_{n}'].iloc[-1]
        if pd.isna(z_val):
            return None
        z_values.append(z_val)

    # Weighted sum (dot product) using ticker-specific weights
    w = ticker_weights['encoder_weight']
    b = ticker_weights['encoder_bias']

    dot = sum(z_values[i] * w[i] for i in range(len(periods))) + b

    # Tanh activation to bound output to [-1, +1]
    signal = float(np.tanh(dot))

    return round(signal, 3)


def get_ztanh_zone(ztanh_value: float, ticker: str = 'default', timeframe: str = 'daily') -> str:
    """
    Classify ZTanh value into a zone based on ticker-specific thresholds.

    Zones (from high to low):
        Extreme OB: Above extreme_ob threshold
        Overbought: Between overbought and extreme_ob
        Upper: Between upper and overbought
        Neutral: Between lower and upper
        Lower: Between oversold and lower
        Oversold: Between extreme_os and oversold
        Extreme OS: Below extreme_os threshold

    Args:
        ztanh_value: ZTanh signal value
        ticker: Ticker symbol for threshold lookup
        timeframe: 'daily' or 'weekly'

    Returns:
        str: Zone classification
    """
    if ztanh_value is None:
        return "N/A"

    t = get_ticker_thresholds(ticker, timeframe)

    if ztanh_value >= t['extreme_ob']:
        return "Extreme OB"
    elif ztanh_value >= t['overbought']:
        return "Overbought"
    elif ztanh_value >= t['upper']:
        return "Upper"
    elif ztanh_value > t['lower']:
        return "Neutral"
    elif ztanh_value > t['oversold']:
        return "Lower"
    elif ztanh_value > t['extreme_os']:
        return "Oversold"
    else:
        return "Extreme OS"


def get_vix_sentiment(ztanh_value: float) -> str:
    """
    Convert VIX ZTanh value to sentiment label.

    VIX ZTanh interpretation:
        Positive = Greed/Complacency (VIX low relative to history)
        Negative = Fear (VIX elevated relative to history)

    Sentiment zones:
        > +0.70: Extreme Greed
        +0.50 to +0.70: Greed
        +0.20 to +0.50: Mild Greed
        -0.20 to +0.20: Neutral
        -0.50 to -0.20: Mild Fear
        -0.70 to -0.50: Fear
        < -0.70: Extreme Fear

    Args:
        ztanh_value: VIX ZTanh signal value

    Returns:
        str: Sentiment classification
    """
    if ztanh_value is None:
        return "N/A"

    if ztanh_value > 0.70:
        return "Extreme Greed"
    elif ztanh_value > 0.50:
        return "Greed"
    elif ztanh_value > 0.20:
        return "Mild Greed"
    elif ztanh_value >= -0.20:
        return "Neutral"
    elif ztanh_value >= -0.50:
        return "Mild Fear"
    elif ztanh_value >= -0.70:
        return "Fear"
    else:
        return "Extreme Fear"
