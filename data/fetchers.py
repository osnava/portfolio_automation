"""API data fetchers for market indicators."""

import requests
import pandas as pd
from data.cache import load_from_cache, save_to_cache, get_cached_ticker
from indicators.rsi_bb import calculate_rsi, get_vix_sentiment
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
    """Fetch current VIX value and calculate RSI. Always fetches fresh data."""
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

    # Calculate RSI for VIX and convert to sentiment label (contrary indicator)
    rsi = calculate_rsi(hist['Close'])
    sentiment = get_vix_sentiment(rsi)

    return vix, rsi, sentiment


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


def get_fx_rate(pair_code, lookback=5):
    """Get latest FX rate from FRED with lookback for holidays.

    Args:
        pair_code: FRED series code for FX rate
        lookback: Number of observations to fetch (handles holidays)

    Returns:
        float: FX rate or None if unavailable
    """
    data = get_fred_series(pair_code, limit=lookback)
    if data:
        # Return most recent non-null value
        for val, date in data:
            if val is not None:
                return val
    return None


def calculate_gli():
    """Calculate Global Liquidity Index: Fed Net + ECB + BOJ + Global M2.

    Formula:
        Net_Fed = FED_BS - TGA - RRP
        GLI = Net_Fed + ECB_BS_USD + BOJ_BS_USD + Global_M2

    All values converted to trillions USD.
    Falls back to US-only if global data unavailable.
    """
    cache_key = "gli"
    cached = load_from_cache(cache_key)
    if cached:
        return cached

    # Fetch US Fed components (weekly)
    fed_data = get_fred_series("WALCL", limit=24)
    tga_data = get_fred_series("WTREGEN", limit=70)
    rrp_data = get_fred_series("RRPONTSYD", limit=180)

    if not all([fed_data, tga_data, rrp_data]):
        return None

    # Fetch FX rates (with 5-day lookback for holidays)
    eurusd = get_fx_rate("DEXUSEU")  # USD per EUR
    usdjpy = get_fx_rate("DEXJPUS")  # JPY per USD
    usdcny = get_fx_rate("DEXCHUS")  # CNY per USD

    # Fetch global central bank data
    ecb_data = get_fred_series("ECBASSETSW", limit=24)  # Weekly, millions EUR
    boj_data = get_fred_series("JPNASSETS", limit=12)   # Monthly, 100 million JPY

    # Fetch M2 data (all monthly)
    usa_m2_data = get_fred_series("M2SL", limit=12)           # Billions USD
    eur_m2_data = get_fred_series("MYAGM2EZM196N", limit=12)  # EUR
    jpy_m2_data = get_fred_series("MYAGM2JPM189S", limit=12)  # JPY
    cny_m2_data = get_fred_series("MYAGM2CNM189N", limit=12)  # CNY

    # Check if we have global data
    has_global = all([
        eurusd, usdjpy, usdcny,
        ecb_data, boj_data,
        usa_m2_data, eur_m2_data, jpy_m2_data, cny_m2_data
    ])

    # Build GLI time series (weekly aligned)
    gli_series = []
    for fed_val, fed_date in fed_data:
        # Find most recent TGA and RRP values on or before fed_date
        tga_val = next((v for v, d in tga_data if d <= fed_date), None)
        rrp_val = next((v for v, d in rrp_data if d <= fed_date), None)
        if tga_val is not None and rrp_val is not None:
            # Net Fed in billions USD
            # WALCL & WTREGEN are in millions USD, RRPONTSYD is in billions USD
            net_fed = (fed_val - tga_val - rrp_val * 1000) / 1000

            if has_global:
                # ECB: millions EUR -> billions USD
                ecb_val = next((v for v, d in ecb_data if d <= fed_date), None)
                ecb_usd = (ecb_val * eurusd / 1000) if ecb_val else 0

                # BOJ: 100 million JPY -> billions USD
                # JPNASSETS is in 100 million JPY, divide by 10 to get billions JPY
                # then divide by JPY/USD rate to get billions USD
                boj_val = next((v for v, d in boj_data if d <= fed_date), None)
                boj_usd = (boj_val / 10 / usdjpy) if boj_val else 0

                # M2 conversions (use most recent available)
                usa_m2 = next((v for v, d in usa_m2_data if d <= fed_date), None) or 0

                eur_m2_val = next((v for v, d in eur_m2_data if d <= fed_date), None)
                eur_m2_usd = (eur_m2_val * eurusd / 1e9) if eur_m2_val else 0

                jpy_m2_val = next((v for v, d in jpy_m2_data if d <= fed_date), None)
                jpy_m2_usd = (jpy_m2_val / usdjpy / 1e9) if jpy_m2_val else 0

                cny_m2_val = next((v for v, d in cny_m2_data if d <= fed_date), None)
                cny_m2_usd = (cny_m2_val / usdcny / 1e9) if cny_m2_val else 0

                global_m2 = usa_m2 + eur_m2_usd + jpy_m2_usd + cny_m2_usd

                # Total GLI in trillions USD
                total_gli = (net_fed + ecb_usd + boj_usd + global_m2) / 1000
                gli_series.append((total_gli, fed_date))
            else:
                # Fallback: US-only (convert to trillions for consistency)
                gli_series.append((net_fed / 1000, fed_date))

    if not gli_series:
        return None

    current_gli, current_date = gli_series[0]

    def calc_change(weeks):
        if len(gli_series) > weeks:
            prev = gli_series[weeks][0]
            if prev != 0:
                change = current_gli - prev
                return round(change, 2), round((change / prev) * 100, 2)
        return None, None

    wow_change, wow_pct = calc_change(1)
    mom_change, mom_pct = calc_change(4)
    qoq_change, qoq_pct = calc_change(12)

    trend = "Expanding" if mom_pct and mom_pct > 1 else "Contracting" if mom_pct and mom_pct < -1 else "Flat"

    # Lagged analysis (10 weeks ago) - markets follow liquidity with ~10 week delay
    lagged_10w_pct = None
    if len(gli_series) > 10:
        gli_10w_ago = gli_series[10][0]
        if gli_10w_ago != 0:
            lagged_10w_pct = round((current_gli - gli_10w_ago) / gli_10w_ago * 100, 2)

    lagged_10w_trend = (
        "expanding" if lagged_10w_pct and lagged_10w_pct > 1 else
        "contracting" if lagged_10w_pct and lagged_10w_pct < -1 else
        "flat"
    )

    # Build component breakdown for transparency
    components = {}
    if has_global:
        # Get latest values for each component
        net_fed_latest = (fed_data[0][0] - tga_data[0][0] - rrp_data[0][0] * 1000) / 1000 / 1000  # Trillions
        ecb_latest = (ecb_data[0][0] * eurusd / 1000 / 1000) if ecb_data else 0  # Trillions
        boj_latest = (boj_data[0][0] / 10 / usdjpy / 1000) if boj_data else 0  # Trillions

        usa_m2_latest = (usa_m2_data[0][0] / 1000) if usa_m2_data else 0  # Trillions
        eur_m2_latest = (eur_m2_data[0][0] * eurusd / 1e9 / 1000) if eur_m2_data else 0
        jpy_m2_latest = (jpy_m2_data[0][0] / usdjpy / 1e9 / 1000) if jpy_m2_data else 0
        cny_m2_latest = (cny_m2_data[0][0] / usdcny / 1e9 / 1000) if cny_m2_data else 0

        components = {
            'net_fed': round(net_fed_latest, 2),
            'ecb': round(ecb_latest, 2),
            'boj': round(boj_latest, 2),
            'usa_m2': round(usa_m2_latest, 2),
            'eur_m2': round(eur_m2_latest, 2),
            'jpy_m2': round(jpy_m2_latest, 2),
            'cny_m2': round(cny_m2_latest, 2),
            'global_m2': round(usa_m2_latest + eur_m2_latest + jpy_m2_latest + cny_m2_latest, 2),
        }

    result = {
        'value': round(current_gli, 2),
        'unit': 'Trillions USD',
        'is_global': has_global,
        'components': components,
        'date': current_date,
        'wow_change': wow_change, 'wow_pct': wow_pct,
        'mom_change': mom_change, 'mom_pct': mom_pct,
        'qoq_change': qoq_change, 'qoq_pct': qoq_pct,
        'trend': trend,
        'lagged_10w_pct': lagged_10w_pct,
        'lagged_10w_trend': lagged_10w_trend,
    }
    save_to_cache(cache_key, result)
    return result
