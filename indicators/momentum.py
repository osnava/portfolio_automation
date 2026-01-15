"""Momentum indicators (TSMOM, MA Score)."""

from config import TSMOM_LOOKBACKS, MA_PERIODS


def calculate_tsmom(close, lookbacks=TSMOM_LOOKBACKS):
    """
    Time-series momentum: average return across lookback periods
    Returns the mean percentage return across all lookback windows
    """
    if len(close) < max(lookbacks):
        return None, []

    returns = []
    details = []
    for lb in lookbacks:
        ret = (close.iloc[-1] / close.iloc[-lb] - 1) * 100
        returns.append(ret)
        details.append(f"{lb}w: {ret:+.1f}%")

    composite = sum(returns) / len(returns)
    return round(composite, 2), details


def calculate_ma_score(close, price):
    """
    MA trend alignment score (0-7):
    - Price vs MA20, MA50, MA100, MA200
    - MA20 vs MA50, MA50 vs MA100, MA100 vs MA200
    """
    if len(close) < 50:
        return None, None, []

    ma20 = close.rolling(20).mean().iloc[-1]
    ma50 = close.rolling(50).mean().iloc[-1]
    ma100 = close.rolling(100).mean().iloc[-1] if len(close) >= 100 else None
    ma200 = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else None

    checks = [
        (price > ma20, "Price>MA20"),
        (price > ma50, "Price>MA50"),
        (ma20 > ma50, "MA20>MA50"),
    ]

    if ma100 is not None:
        checks.extend([
            (price > ma100, "Price>MA100"),
            (ma50 > ma100, "MA50>MA100"),
        ])

    if ma200 is not None:
        checks.extend([
            (price > ma200, "Price>MA200"),
            (ma100 > ma200 if ma100 else ma50 > ma200, "MA100>MA200" if ma100 else "MA50>MA200"),
        ])

    score = sum(1 for cond, _ in checks if cond)
    max_score = len(checks)
    details = [name for cond, name in checks if cond]

    return score, max_score, details


def format_ma_distance(close, price, periods=MA_PERIODS):
    """Calculate distance from MAs."""
    parts = []
    for p in periods:
        if len(close) >= p:
            ma = close.rolling(p).mean().iloc[-1]
            pct = ((price - ma) / ma) * 100
            parts.append(f"MA{p}: {abs(pct):.1f}%{'↑' if pct > 0 else '↓'}")
    return " | ".join(parts) if parts else "N/A"
