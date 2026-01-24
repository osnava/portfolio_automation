"""Market regime classification for strategy selection."""

from config import ADX_NO_TREND, ADX_TREND_EMERGING
from indicators.ztanh import get_ticker_thresholds


def classify_regime(adx, tsmom_score, ztanh, ticker='default'):
    """
    Classify market regime. Returns (regime, mode).

    ADX Levels:
        > 25: Strong trend → trend-following mode
        20-25: Emerging trend → cautious trend-following
        < 20: No trend → mean-reversion mode

    TSMOM Levels:
        > +2%: Positive momentum
        < -2%: Negative momentum
        [-2%, +2%]: Neutral momentum

    Args:
        adx: ADX indicator value
        tsmom_score: Time-series momentum score (%)
        ztanh: ZTanh indicator value [-1, +1]
        ticker: Ticker symbol for threshold lookup

    Returns:
        tuple: (regime_name, mode_description)
    """
    if adx is None or tsmom_score is None:
        return "Unknown", "Insufficient data"

    # Get ticker-specific thresholds for weekly timeframe
    thresholds = get_ticker_thresholds(ticker, timeframe='weekly')

    # === STRONG TREND: ADX > 25 ===
    if adx > ADX_TREND_EMERGING:
        # Bullish: positive momentum
        if tsmom_score > 2:
            return "Trending Up", "Trend-following: long"
        # Bearish: negative momentum
        if tsmom_score < -2:
            return "Trending Down", "Trend-following: exit"
        # ADX > 25 but momentum neutral
        return "Trend Unclear", "Trend present, signals mixed"

    # === EMERGING TREND: ADX 20-25 ===
    if adx >= ADX_NO_TREND:
        if tsmom_score > 2:
            return "Emerging Up", "Emerging trend: cautious long"
        if tsmom_score < -2:
            return "Emerging Down", "Emerging trend: cautious exit"
        return "Neutral", "No clear edge"

    # === NO TREND: ADX < 20 → mean-reversion mode ===
    if ztanh is not None:
        if ztanh <= thresholds['oversold']:
            return "Mean Revert Buy", "Mean-reversion: long"
        if ztanh >= thresholds['overbought']:
            return "Mean Revert Sell", "Mean-reversion: short"

    return "Choppy", "No-trade mode"
