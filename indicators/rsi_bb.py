"""RSI and Bollinger Bands indicators using ta library."""

import pandas as pd
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands


def calculate_rsi(close: pd.Series, period: int = 14) -> float:
    """
    Calculate RSI (Relative Strength Index) using ta library.

    Args:
        close: Price series (pd.Series)
        period: RSI lookback period (default 14)

    Returns:
        RSI value (0-100), or None if insufficient data
    """
    if len(close) < period + 10:
        return None

    rsi_indicator = RSIIndicator(close, window=period)
    rsi_series = rsi_indicator.rsi()
    rsi_value = rsi_series.iloc[-1]

    if pd.isna(rsi_value):
        return None

    return round(rsi_value, 2)


def get_rsi_zone(rsi: float) -> str:
    """
    Classify RSI value into a zone.

    Standard RSI interpretation:
        > 70: Overbought
        30-70: Neutral
        < 30: Oversold

    Args:
        rsi: RSI value (0-100)

    Returns:
        str: Zone classification
    """
    if rsi is None:
        return "N/A"

    if rsi >= 70:
        return "Overbought"
    elif rsi <= 30:
        return "Oversold"
    else:
        return "Neutral"


def get_vix_sentiment(rsi: float) -> str:
    """
    Convert VIX RSI to sentiment label (contrary indicator).

    VIX RSI interpretation (CONTRARY):
        High VIX RSI = High VIX = Fear = BUY opportunity
        Low VIX RSI = Low VIX = Greed = SELL/Caution

    Sentiment zones:
        > 80: Extreme Fear (Strong contrarian BUY)
        70-80: Fear (Contrarian BUY)
        60-70: Mild Fear (Pullback opportunity)
        40-60: Neutral (Standard ops)
        30-40: Mild Greed (Caution)
        20-30: Greed (Trim longs)
        < 20: Extreme Greed (High caution)

    Args:
        rsi: VIX RSI value (0-100)

    Returns:
        str: Sentiment classification
    """
    if rsi is None:
        return "N/A"

    if rsi > 80:
        return "Extreme Fear"
    elif rsi > 70:
        return "Fear"
    elif rsi > 60:
        return "Mild Fear"
    elif rsi >= 40:
        return "Neutral"
    elif rsi >= 30:
        return "Mild Greed"
    elif rsi >= 20:
        return "Greed"
    else:
        return "Extreme Greed"


def calculate_bollinger_bands(close: pd.Series, period: int = 20) -> dict:
    """
    Calculate Bollinger Bands at 1, 2, 3 standard deviations.

    Args:
        close: Price series (pd.Series)
        period: Moving average period (default 20)

    Returns:
        dict with bands at each STD level, or None if insufficient data
    """
    if len(close) < period + 10:
        return None

    # Calculate bands at different standard deviations
    bb_1 = BollingerBands(close, window=period, window_dev=1)
    bb_2 = BollingerBands(close, window=period, window_dev=2)
    bb_3 = BollingerBands(close, window=period, window_dev=3)

    return {
        'middle': bb_2.bollinger_mavg().iloc[-1],
        'upper_1': bb_1.bollinger_hband().iloc[-1],
        'lower_1': bb_1.bollinger_lband().iloc[-1],
        'upper_2': bb_2.bollinger_hband().iloc[-1],
        'lower_2': bb_2.bollinger_lband().iloc[-1],
        'upper_3': bb_3.bollinger_hband().iloc[-1],
        'lower_3': bb_3.bollinger_lband().iloc[-1],
    }


def get_bb_position(price: float, bands: dict) -> str:
    """
    Classify price position relative to Bollinger Bands.

    Args:
        price: Current price
        bands: Dict with BB levels from calculate_bollinger_bands()

    Returns:
        str: Position classification
    """
    if bands is None or price is None:
        return "N/A"

    if price > bands['upper_3']:
        return "Above +3 STD"
    elif price > bands['upper_2']:
        return "Above +2 STD"
    elif price > bands['upper_1']:
        return "Above +1 STD"
    elif price >= bands['lower_1']:
        return "Within Bands"
    elif price >= bands['lower_2']:
        return "Below -1 STD"
    elif price >= bands['lower_3']:
        return "Below -2 STD"
    else:
        return "Below -3 STD"
