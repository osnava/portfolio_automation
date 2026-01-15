"""TEMA (Triple Exponential Moving Average) and ensemble calculations."""

import numpy as np
import pandas as pd
from config import (
    TEMA_BASE_PERIODS,
    VOLATILITY_LOOKBACK,
    VOLATILITY_ATR_PERIOD,
    VOLATILITY_SCALAR_MIN,
    VOLATILITY_SCALAR_MAX
)


def calculate_tema(series, period):
    """
    Calculate Triple Exponential Moving Average (TEMA).
    TEMA = 3*EMA - 3*EMA(EMA) + EMA(EMA(EMA))
    More responsive than EMA, less lag.
    """
    ema1 = series.ewm(span=period, adjust=False).mean()
    ema2 = ema1.ewm(span=period, adjust=False).mean()
    ema3 = ema2.ewm(span=period, adjust=False).mean()
    tema = 3 * ema1 - 3 * ema2 + ema3
    return tema


def get_volatility_scalar(close, lookback=VOLATILITY_LOOKBACK):
    """
    Calculate volatility scalar for adaptive period selection.
    Returns ratio of current ATR vs historical median ATR.

    High volatility (ratio > 1) → use longer periods to filter noise
    Low volatility (ratio < 1) → use shorter periods to capture moves

    Clamped to [0.5, 2.0] to prevent extreme period adjustments.
    """
    if len(close) < lookback:
        return 1.0  # Default to no adjustment if insufficient data

    # Calculate ATR (14-day rolling mean of absolute returns)
    atr = close.diff().abs().rolling(VOLATILITY_ATR_PERIOD).mean()

    # Current ATR vs historical median
    atr_current = atr.iloc[-1]
    atr_historical = atr.rolling(lookback).median().iloc[-1]

    if atr_historical == 0 or pd.isna(atr_historical):
        return 1.0

    ratio = atr_current / atr_historical

    # Clamp to prevent extreme values
    return np.clip(ratio, VOLATILITY_SCALAR_MIN, VOLATILITY_SCALAR_MAX)


def calculate_tema_ensemble(close, price):
    """
    Multi-period TEMA ensemble with volatility adjustment.

    Calculates TEMA alignment across 3 period sets (fast/standard/slow),
    adjusted by current volatility. Returns consensus signal and confidence.

    Returns:
        - consensus: -1.0 to +1.0 (signal strength)
        - confidence: 0.0 to 1.0 (agreement level)
        - ensemble_str: "X/3" format (e.g., "3/3", "2/3")
        - detail: Human-readable breakdown
        - vol_scalar: Volatility adjustment factor
    """
    # Get volatility scalar
    vol_scalar = get_volatility_scalar(close)

    # Apply volatility adjustment
    adjusted_periods = [
        (int(fast * vol_scalar), int(mid * vol_scalar), int(slow * vol_scalar))
        for fast, mid, slow in TEMA_BASE_PERIODS
    ]

    alignment_signals = []
    details = []

    for (p_fast, p_mid, p_slow), (base_fast, base_mid, base_slow) in zip(adjusted_periods, TEMA_BASE_PERIODS):
        # Calculate TEMAs for this period set
        try:
            tema_fast = calculate_tema(close, p_fast).iloc[-1]
            tema_mid = calculate_tema(close, p_mid).iloc[-1]
            tema_slow = calculate_tema(close, p_slow).iloc[-1]
        except:
            # Skip this period set if calculation fails
            continue

        # Count bullish/bearish components
        score = 0
        if price > tema_fast:
            score += 1
        if tema_fast > tema_mid:
            score += 1
        if tema_mid > tema_slow:
            score += 1

        # Convert to signal: 3=bullish, 0=bearish, else=mixed
        if score == 3:
            signal = +1  # All bullish
        elif score == 0:
            signal = -1  # All bearish
        else:
            signal = 0   # Mixed

        alignment_signals.append(signal)

        # Detail string showing base periods and signal
        signal_str = "+" if signal > 0 else ("-" if signal < 0 else "~")
        details.append(f"{base_fast}/{base_mid}/{base_slow}:{signal_str}")

    # Calculate consensus and confidence
    if not alignment_signals:
        return 0.0, 0.0, "0/3", "Error", vol_scalar

    consensus = sum(alignment_signals) / len(alignment_signals)
    confidence = abs(consensus)

    # Count strong signals
    bullish_count = sum(1 for s in alignment_signals if s > 0)
    bearish_count = sum(1 for s in alignment_signals if s < 0)

    if consensus > 0:
        ensemble_str = f"{bullish_count}/3"
    elif consensus < 0:
        ensemble_str = f"-{bearish_count}/3"
    else:
        ensemble_str = "0/3"

    detail = " | ".join(details)

    return round(consensus, 2), round(confidence, 2), ensemble_str, detail, round(vol_scalar, 2)


def detect_cross(ma_fast, ma_fast_prev, ma_slow, ma_slow_prev):
    """
    Detect MA crossover.
    Returns: "Bullish Cross", "Bearish Cross", or "None"
    """
    if ma_fast > ma_slow and ma_fast_prev <= ma_slow_prev:
        return "Bullish Cross"
    elif ma_fast < ma_slow and ma_fast_prev >= ma_slow_prev:
        return "Bearish Cross"
    return "None"
