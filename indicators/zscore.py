"""Z-score calculations for mean reversion analysis."""

import numpy as np
import pandas as pd
from config import ZSCORE_WINDOW


def calculate_zscore(close, window=ZSCORE_WINDOW):
    """Calculate z-score for price series."""
    if len(close) < window:
        return None, None

    mean = float(close.rolling(window).mean().iloc[-1])
    std = float(close.rolling(window).std().iloc[-1])

    if std == 0 or pd.isna(std):
        return 0, "Neutral"

    zscore = round((float(close.iloc[-1]) - mean) / std, 2)

    # Classify zone using threshold ranges
    zones = [
        (2.5, float('inf'), "Extreme OB"),
        (2, 2.5, "Overbought"),
        (1, 2, "Upper"),
        (-1, 1, "Neutral"),
        (-2, -1, "Lower"),
        (-2.5, -2, "Oversold"),
        (float('-inf'), -2.5, "Extreme OS"),
    ]

    zone = next((z for low, high, z in zones if low <= zscore < high), "Neutral")
    return zscore, zone
