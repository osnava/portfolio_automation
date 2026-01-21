"""API data fetchers for market indicators."""

import requests
import pandas as pd
from data.cache import load_from_cache, save_to_cache, get_cached_ticker
from indicators.ztanh import calculate_ztanh, get_vix_sentiment
from config import FRED_API_KEY


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


def get_vix():
    """Fetch current VIX value and calculate ZTanh. Always fetches fresh data."""
    import yfinance as yf

    # Always fetch fresh VIX data (no caching - VIX is critical and yfinance is fast)
    try:
        hist = yf.download("^VIX", period="1y", interval="1d", auto_adjust=True, progress=False)
        if isinstance(hist.columns, pd.MultiIndex):
            hist.columns = hist.columns.get_level_values(0)
    except Exception:
        hist = pd.DataFrame()

    if hist.empty or len(hist) < 210:
        return None, None, None

    vix = round(hist['Close'].iloc[-1], 2)

    # Calculate ZTanh for VIX using VIX-specific weights and convert to sentiment label
    ztanh = calculate_ztanh(hist['Close'], ticker='^VIX')
    sentiment = get_vix_sentiment(ztanh)

    return vix, ztanh, sentiment


def get_vix_level(vix):
    """
    Classify VIX into a regime level.

    Args:
        vix: VIX value

    Returns:
        str: VIX level description
    """
    if vix is None:
        return "N/A"

    if vix < 15:
        return "Low"
    elif vix < 20:
        return "Normal"
    elif vix < 30:
        return "Elevated"
    else:
        return "High"


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

    trend = "Expanding" if mom_pct and mom_pct > 1 else "Contracting" if mom_pct and mom_pct < -1 else "Flat"

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
