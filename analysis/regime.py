"""Market regime classification for strategy selection."""


def classify_regime(adx, tsmom_score, zscore, ma_score, ma_max):
    """
    Classify market regime for strategy selection.
    Returns: regime name, action bias

    tsmom_score is the average % return across lookback periods
    """
    if adx is None or tsmom_score is None:
        return "UNKNOWN", "Insufficient data"

    ma_pct = (ma_score / ma_max) if ma_max > 0 else 0

    # Strong uptrend: high ADX + positive momentum + good MA alignment
    if adx > 25 and tsmom_score > 2 and ma_pct >= 0.6:
        return "TRENDING_UP", "Ride trend, buy dips"

    # Strong downtrend: high ADX + negative momentum
    if adx > 25 and tsmom_score < -2:
        return "TRENDING_DOWN", "Avoid or exit"

    # Mean-reversion opportunity: weak trend + extreme Z
    if adx < 25 and zscore is not None and abs(zscore) > 1.5:
        if zscore < -1.5:
            return "MEAN_REVERT_BUY", "Z-score oversold"
        else:
            return "MEAN_REVERT_SELL", "Z-score overbought"

    # Choppy/unclear
    if adx < 20:
        return "CHOPPY", "Reduce exposure, wait"

    return "NEUTRAL", "No strong edge"
