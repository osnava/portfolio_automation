"""API data fetchers for market indicators."""

import requests
from data.cache import load_from_cache, save_to_cache, get_cached_ticker
from config import FRED_API_KEY, VIX_ZSCORE_WINDOW, VIX_ZSCORE_EMA_SPAN


def get_fred_series(series_id, limit=1):
    """Fetch values from FRED API."""
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": limit,
    }
    r = requests.get("https://api.stlouisfed.org/fred/series/observations", params=params, timeout=10)
    r.raise_for_status()

    observations = r.json().get('observations', [])
    if not observations:
        return (None, None) if limit == 1 else []

    if limit == 1:
        return float(observations[0]['value']), observations[0]['date']

    return [(float(o['value']), o['date']) for o in observations if o['value'] != '.']


def get_fear_greed_traditional():
    """Fetch CNN Fear & Greed Index using fear-and-greed package."""
    cache_key = "fear_greed_stocks"
    cached = load_from_cache(cache_key)
    if cached:
        return cached['value'], cached['description']

    try:
        import fear_and_greed
    except ImportError:
        raise ImportError(
            "fear-and-greed package not installed.\n"
            "Install with: pip install fear-and-greed"
        )

    data = fear_and_greed.get()
    result = {'value': round(data.value), 'description': data.description.title()}
    save_to_cache(cache_key, result)
    return result['value'], result['description']


def get_fear_greed_crypto():
    """Fetch Crypto Fear & Greed Index."""
    cache_key = "fear_greed_crypto"
    cached = load_from_cache(cache_key)
    if cached:
        return cached['value'], cached['classification']

    r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=10)
    r.raise_for_status()
    data = r.json()['data'][0]
    result = {'value': int(data['value']), 'classification': data['value_classification'].title()}
    save_to_cache(cache_key, result)
    return result['value'], result['classification']


def get_vix_zscore():
    """Fetch VIX and calculate smoothed inverted Z-score (252-day rolling window, 5-period EMA)."""
    cache_key = "vix_zscore"
    cached = load_from_cache(cache_key)
    if cached:
        return cached['vix'], cached['z_score']

    hist = get_cached_ticker("^VIX", period="2y", interval="1d")
    if hist.empty or len(hist) < VIX_ZSCORE_WINDOW:
        return None, None

    vix_series = hist['Close']
    vix = round(vix_series.iloc[-1], 2)

    # Z-score with 252-day window (1 year of trading days)
    mean = vix_series.rolling(VIX_ZSCORE_WINDOW).mean()
    std = vix_series.rolling(VIX_ZSCORE_WINDOW).std()
    z = (vix_series - mean) / std

    # Invert and smooth with 5-period EMA
    z_inverted = -z
    z_smooth = z_inverted.ewm(span=VIX_ZSCORE_EMA_SPAN, adjust=False).mean()

    z_score = round(z_smooth.iloc[-1], 2)
    result = {'vix': vix, 'z_score': z_score}
    save_to_cache(cache_key, result)
    return vix, z_score


def calculate_gli():
    """Calculate Global Liquidity Index: Fed Balance Sheet - TGA - RRP."""
    cache_key = "gli"
    cached = load_from_cache(cache_key)
    if cached:
        return cached

    fed_data = get_fred_series("WALCL", limit=14)
    tga_data = get_fred_series("WTREGEN", limit=70)
    rrp_data = get_fred_series("RRPONTSYD", limit=70)

    if not all([fed_data, tga_data, rrp_data]):
        return None

    gli_series = []
    for fed_val, fed_date in fed_data:
        # Find most recent TGA and RRP values on or before fed_date
        tga_val = next((v for v, d in tga_data if d <= fed_date), None)
        rrp_val = next((v for v, d in rrp_data if d <= fed_date), None)
        if tga_val and rrp_val:
            gli_series.append(((fed_val - tga_val - rrp_val) / 1000, fed_date))

    if not gli_series:
        return None

    current_gli, current_date = gli_series[0]

    def calc_change(weeks):
        if len(gli_series) > weeks:
            prev = gli_series[weeks][0]
            change = current_gli - prev
            return round(change, 2), round((change / prev) * 100, 2)
        return None, None

    wow_change, wow_pct = calc_change(1)
    mom_change, mom_pct = calc_change(4)
    qoq_change, qoq_pct = calc_change(12)

    trend = "📈 Expanding" if mom_pct and mom_pct > 1 else "📉 Contracting" if mom_pct and mom_pct < -1 else "➡️ Flat"

    result = {
        'value': round(current_gli, 2),
        'fed_bs': round(fed_data[0][0] / 1000, 2),
        'tga': round(tga_data[0][0] / 1000, 2),
        'rrp': round(rrp_data[0][0] / 1000, 2),
        'date': current_date,
        'wow_change': wow_change, 'wow_pct': wow_pct,
        'mom_change': mom_change, 'mom_pct': mom_pct,
        'qoq_change': qoq_change, 'qoq_pct': qoq_pct,
        'trend': trend,
    }
    save_to_cache(cache_key, result)
    return result


def get_regime_from_vix_z(vix_z):
    """Map VIX Z-score to market regime."""
    if vix_z >= 1.5:
        return "Complacency"
    elif vix_z <= -1.5:
        return "Fear"
    elif vix_z >= 0.5:
        return "Risk-On"
    elif vix_z <= -0.5:
        return "Risk-Off"
    return "Neutral"
