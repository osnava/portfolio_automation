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


def _convert_to_billions_usd(value, fx_rate, fx_mode, scale):
    """Convert a national-currency value to billions USD.

    Args:
        value: Raw FRED observation value
        fx_rate: FX rate from FRED
        fx_mode: 'multiply' (val * rate = USD), 'divide' (val / rate = USD), or None
        scale: Multiplier to normalize units (e.g., 1e-9 for raw currency → billions)

    Returns:
        float: Value in billions USD
    """
    if fx_mode is None:
        return value * scale  # Already in USD (M2SL is billions, scale=1)
    elif fx_mode == 'multiply':
        return value * fx_rate * scale
    else:  # divide
        return value / fx_rate * scale


def calculate_gli():
    """Calculate Global Liquidity Index from central bank balance sheets + broad money.

    Formula:
        Net_Fed = FED_BS - TGA - RRP
        GLI = Net_Fed + ECB_BS_USD + BOJ_BS_USD + Global_Broad_Money

    Broad money covers 12 economies (USA, Eurozone, Japan, China, UK, Canada,
    Australia, India, Switzerland, Brazil, South Korea, Mexico).
    All values converted to trillions USD.
    Falls back to US-only if global data unavailable.
    """
    from config import GLI_BROAD_MONEY

    cache_key = "gli"
    cached = load_from_cache(cache_key)
    if cached:
        return cached

    # --- Fetch US Fed components (weekly) ---
    fed_data = get_fred_series("WALCL", limit=24)
    tga_data = get_fred_series("WTREGEN", limit=70)
    rrp_data = get_fred_series("RRPONTSYD", limit=180)

    if not all([fed_data, tga_data, rrp_data]):
        return None

    # --- Fetch all FX rates (with 5-day lookback for holidays) ---
    fx_rates = {}
    fx_needed = set()
    for cfg in GLI_BROAD_MONEY.values():
        if cfg['fx']:
            fx_needed.add(cfg['fx'])
    # Also need EUR/USD and JPY/USD for ECB and BOJ balance sheets
    fx_needed.update(['DEXUSEU', 'DEXJPUS'])

    for fx_code in fx_needed:
        fx_rates[fx_code] = get_fx_rate(fx_code)

    eurusd = fx_rates.get('DEXUSEU')
    usdjpy = fx_rates.get('DEXJPUS')

    # --- Fetch central bank balance sheet data ---
    ecb_data = get_fred_series("ECBASSETSW", limit=24)  # Weekly, millions EUR
    boj_data = get_fred_series("JPNASSETS", limit=12)    # Monthly, 100 million JPY

    # --- Fetch broad money data for all configured economies ---
    money_data = {}  # key -> [(value, date), ...]
    money_ok = {}    # key -> bool (has data + FX rate)
    for key, cfg in GLI_BROAD_MONEY.items():
        try:
            data = get_fred_series(cfg['series'], limit=12)
        except Exception:
            data = []
        money_data[key] = data if data else []

        # Check if we can convert this series
        if cfg['fx']:
            money_ok[key] = bool(data) and fx_rates.get(cfg['fx']) is not None
        else:
            money_ok[key] = bool(data)

    # Core 4 must be present for "global" status
    has_global = all([
        eurusd, usdjpy,
        ecb_data, boj_data,
        money_ok.get('usa'), money_ok.get('eur'),
        money_ok.get('jpn'), money_ok.get('chn'),
    ])

    # --- Build GLI time series (weekly aligned to Fed data) ---
    gli_series = []
    for fed_val, fed_date in fed_data:
        tga_val = next((v for v, d in tga_data if d <= fed_date), None)
        rrp_val = next((v for v, d in rrp_data if d <= fed_date), None)
        if tga_val is None or rrp_val is None:
            continue

        # Net Fed in billions USD
        # WALCL & WTREGEN are in millions USD, RRPONTSYD is in billions USD
        net_fed = (fed_val - tga_val - rrp_val * 1000) / 1000

        if has_global:
            # ECB: millions EUR -> billions USD
            ecb_val = next((v for v, d in ecb_data if d <= fed_date), None)
            ecb_usd = (ecb_val * eurusd / 1000) if ecb_val else 0

            # BOJ: 100 million JPY -> billions USD
            boj_val = next((v for v, d in boj_data if d <= fed_date), None)
            boj_usd = (boj_val / 10 / usdjpy) if boj_val else 0

            # Sum all broad money components
            total_money = 0.0
            for key, cfg in GLI_BROAD_MONEY.items():
                if not money_ok.get(key):
                    continue
                val = next((v for v, d in money_data[key] if d <= fed_date), None)
                if val is None:
                    # Use most recent available (stale data better than zero)
                    val = money_data[key][0][0] if money_data[key] else None
                if val is not None:
                    fx = fx_rates.get(cfg['fx']) if cfg['fx'] else None
                    total_money += _convert_to_billions_usd(val, fx, cfg['fx_mode'], cfg['scale'])

            total_gli = (net_fed + ecb_usd + boj_usd + total_money) / 1000
            gli_series.append((total_gli, fed_date))
        else:
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

    # --- Build component breakdown for transparency ---
    components = {}
    if has_global:
        net_fed_latest = (fed_data[0][0] - tga_data[0][0] - rrp_data[0][0] * 1000) / 1e6  # Trillions
        ecb_latest = (ecb_data[0][0] * eurusd / 1e6) if ecb_data else 0
        boj_latest = (boj_data[0][0] / 10 / usdjpy / 1000) if boj_data else 0

        components = {
            'net_fed': round(net_fed_latest, 2),
            'ecb': round(ecb_latest, 2),
            'boj': round(boj_latest, 2),
        }

        # Add each broad money component in trillions
        total_money_t = 0.0
        for key, cfg in GLI_BROAD_MONEY.items():
            if not money_ok.get(key):
                continue
            val = money_data[key][0][0] if money_data[key] else None
            if val is not None:
                fx = fx_rates.get(cfg['fx']) if cfg['fx'] else None
                billions = _convert_to_billions_usd(val, fx, cfg['fx_mode'], cfg['scale'])
                trillions = billions / 1000
                components[f'{key}_m'] = round(trillions, 2)
                total_money_t += trillions

        components['broad_money'] = round(total_money_t, 2)
        components['n_economies'] = sum(1 for k in GLI_BROAD_MONEY if money_ok.get(k))

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
