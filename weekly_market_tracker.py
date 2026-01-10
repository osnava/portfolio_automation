#!/usr/bin/env python3
"""Weekly Market Analysis Tracker"""

import json
import os
import sys
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv
from ta.trend import ADXIndicator
import csv

warnings.filterwarnings('ignore')

# Load environment variables from .env file
load_dotenv()

# CONFIGURATION

FRED_API_KEY = os.getenv("FRED_API_KEY")
if not FRED_API_KEY:
    raise ValueError("FRED_API_KEY environment variable is not set. Please check your .env file.")

# Default assets file
SCRIPT_DIR = Path(__file__).parent
DEFAULT_ASSETS_FILE = SCRIPT_DIR / "assets.json"


def load_assets(file_path=None):
    """Load assets from JSON file."""
    if file_path is None:
        file_path = DEFAULT_ASSETS_FILE
    else:
        file_path = Path(file_path)

    if not file_path.exists():
        print(f"Error: Assets file not found: {file_path}")
        sys.exit(1)

    with open(file_path, 'r') as f:
        return json.load(f)

MA_PERIODS = [20, 50, 100, 200]
ZSCORE_WINDOW = 20

# DATA FETCHING

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
    import fear_and_greed
    data = fear_and_greed.get()
    return round(data.value), data.description.title()


def get_fear_greed_crypto():
    """Fetch Crypto Fear & Greed Index."""
    r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=10)
    r.raise_for_status()
    data = r.json()['data'][0]
    return int(data['value']), data['value_classification'].title()


def get_vix_zscore():
    """Fetch VIX and calculate smoothed inverted Z-score (252-day rolling window, 5-period EMA)."""
    hist = yf.download("^VIX", period="2y", interval="1d", progress=False)
    if hist.empty or len(hist) < 252:
        return None, None

    if isinstance(hist.columns, pd.MultiIndex):
        hist.columns = hist.columns.get_level_values(0)

    vix_series = hist['Close']
    vix = round(vix_series.iloc[-1], 2)

    # Z-score with 252-day window (1 year of trading days)
    mean = vix_series.rolling(252).mean()
    std = vix_series.rolling(252).std()
    z = (vix_series - mean) / std

    # Invert and smooth with 5-period EMA
    z_inverted = -z
    z_smooth = z_inverted.ewm(span=5, adjust=False).mean()

    return vix, round(z_smooth.iloc[-1], 2)


# GLI CALCULATION

def calculate_gli():
    """Calculate Global Liquidity Index: Fed Balance Sheet - TGA - RRP."""
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
    
    return {
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


# TECHNICAL ANALYSIS

def calculate_tsmom(close, lookbacks=[4, 12, 26]):
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


def classify_regime(adx, tsmom_score, zscore, ma_score, ma_max):
    """
    Classify market regime for strategy selection.
    Returns: regime name, action bias

    tsmom_score is now the average % return across lookback periods
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


def calculate_zscore(close, window=ZSCORE_WINDOW):
    """Calculate z-score for price series."""
    if len(close) < window:
        return None, None

    mean = close.rolling(window).mean().iloc[-1]
    std = close.rolling(window).std().iloc[-1]

    if std == 0 or np.isnan(std):
        return 0, "Neutral"

    zscore = round((close.iloc[-1] - mean) / std, 2)

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


def format_ma_distance(close, price, periods):
    """Calculate distance from MAs."""
    parts = []
    for p in periods:
        if len(close) >= p:
            ma = close.rolling(p).mean().iloc[-1]
            pct = ((price - ma) / ma) * 100
            parts.append(f"MA{p}: {abs(pct):.1f}%{'↑' if pct > 0 else '↓'}")
    return " | ".join(parts) if parts else "N/A"


def detect_trend(df):
    """Detect trend using MAs, ADX, and directional indicators."""
    if len(df) < 50:
        return "Insufficient Data", "N/A", None

    close, high, low = df['Close'], df['High'], df['Low']
    price = close.iloc[-1]

    ma20 = close.rolling(20).mean().iloc[-1]
    ma50 = close.rolling(50).mean().iloc[-1]
    ma100 = close.rolling(100).mean().iloc[-1] if len(close) >= 100 else None
    ma200 = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else None

    adx_ind = ADXIndicator(high, low, close, window=14)
    adx = adx_ind.adx().iloc[-1]
    plus_di, minus_di = adx_ind.adx_pos().iloc[-1], adx_ind.adx_neg().iloc[-1]

    score = sum([
        1 if price > ma20 else -1,
        1 if price > ma50 else -1,
        1 if ma20 > ma50 else -1,
        1 if plus_di > minus_di else -1,
    ])
    if ma100 is not None:
        score += (1 if price > ma100 else -1) + (1 if ma50 > ma100 else -1)
    if ma200 is not None:
        ma_above_200 = ma100 > ma200 if ma100 else ma50 > ma200
        score += (1 if price > ma200 else -1) + (1 if ma_above_200 else -1)
    
    if adx < 20:
        return "↔️ Sideways/Choppy", "Weak", round(adx, 1)
    
    strength = "Moderate" if adx < 25 else "Strong"
    threshold = 3 if adx < 25 else 2
    
    if score >= threshold:
        trend = "📈 Uptrend"
    elif score <= -threshold:
        trend = "📉 Downtrend"
    else:
        trend = "↔️ Sideways/Choppy"
    
    return trend, strength, round(adx, 1)


def calculate_technicals(ticker):
    """Calculate technical indicators using weekly timeframe only."""
    # Try 5y for MA200 weekly, fallback to 2y if insufficient
    data = yf.download(ticker, period="5y", interval="1d", progress=False)

    if data.empty or len(data) < 50:
        # Fallback: try shorter period
        data = yf.download(ticker, period="2y", interval="1d", progress=False)

    if data.empty:
        return None

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Get current price from daily close
    price = data['Close'].iloc[-1]

    # Resample to weekly
    weekly_df = data.resample('W').agg({
        'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
    }).dropna()

    weeks_available = len(weekly_df)

    if weeks_available < 26:
        return {
            'price': price,
            'weeks': weeks_available,
            'zscore': None,
            'zscore_zone': 'N/A',
            'ma_distance': 'N/A',
            'trend': 'Insufficient Data',
            'trend_strength': 'N/A',
            'adx': None,
            'tsmom_score': None,
            'tsmom_details': [],
            'ma_score': None,
            'ma_max': None,
            'ma_details': [],
            'regime': 'UNKNOWN',
            'regime_bias': 'Insufficient data'
        }

    # Calculate indicators on weekly data
    close_weekly = weekly_df['Close']
    zscore, zone = calculate_zscore(close_weekly)
    ma_distance = format_ma_distance(close_weekly, price, MA_PERIODS)

    if len(weekly_df) >= 50:
        trend, trend_strength, adx = detect_trend(weekly_df)
    else:
        trend, trend_strength, adx = "Insufficient Data", "N/A", None

    # Trend-following indicators
    tsmom_score, tsmom_details = calculate_tsmom(close_weekly)
    ma_score, ma_max, ma_details = calculate_ma_score(close_weekly, price)

    # Regime classification
    regime, regime_bias = classify_regime(adx, tsmom_score, zscore, ma_score, ma_max)

    return {
        'price': price,
        'weeks': weeks_available,
        'zscore': zscore,
        'zscore_zone': zone,
        'ma_distance': ma_distance,
        'trend': trend,
        'trend_strength': trend_strength,
        'adx': adx,
        'tsmom_score': tsmom_score,
        'tsmom_details': tsmom_details,
        'ma_score': ma_score,
        'ma_max': ma_max,
        'ma_details': ma_details,
        'regime': regime,
        'regime_bias': regime_bias
    }


# HELPERS

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


def format_sign(value):
    """Format number with + or - sign."""
    return f"{'+' if value >= 0 else ''}{value}"


# MAIN

def main():
    # Parse command line argument for assets file
    assets_file = sys.argv[1] if len(sys.argv) > 1 else None
    ASSETS = load_assets(assets_file)

    # Get assets file name for display
    assets_name = Path(assets_file).stem if assets_file else "assets"

    # Generate timestamp-based filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = SCRIPT_DIR / "output"
    output_dir.mkdir(exist_ok=True)

    print(f"Fetching market data...")
    print(f"Date: {datetime.now().strftime('%A, %Y-%m-%d %H:%M')}")
    print(f"Portfolio: {assets_name}")

    # Collect macro data
    macro_data = []

    # GLI
    print("Fetching GLI data...")
    try:
        if gli := calculate_gli():
            macro_data.append({
                'Indicator': 'Global Liquidity',
                'Value': f"${gli['value']:,.0f}B",
                'Signal': gli['trend'],
                'Detail': f"4w: {format_sign(gli['mom_pct'])}% | 12w: {format_sign(gli['qoq_pct'])}%"
            })
        else:
            macro_data.append({'Indicator': 'Global Liquidity', 'Value': 'Error', 'Signal': '-', 'Detail': '-'})
    except Exception:
        macro_data.append({'Indicator': 'Global Liquidity', 'Value': 'Error', 'Signal': '-', 'Detail': '-'})

    # VIX
    print("Fetching VIX data...")
    try:
        vix, vix_z = get_vix_zscore()
        if vix:
            vix_levels = [(15, "Low"), (20, "Normal"), (30, "Elevated"), (float('inf'), "High")]
            vix_desc = next(desc for threshold, desc in vix_levels if vix < threshold)
            regime = get_regime_from_vix_z(vix_z)
            macro_data.append({'Indicator': 'VIX', 'Value': vix, 'Signal': vix_desc, 'Detail': ''})
            macro_data.append({'Indicator': '-Z(VIX)', 'Value': f"{vix_z:+.2f}", 'Signal': regime, 'Detail': ''})
    except Exception:
        macro_data.append({'Indicator': 'VIX', 'Value': 'Error', 'Signal': '-', 'Detail': '-'})

    # Fear & Greed
    print("Fetching Fear & Greed indices...")
    for fn, lbl in [(get_fear_greed_traditional, 'F&G Stocks'), (get_fear_greed_crypto, 'F&G Crypto')]:
        try:
            val, cls = fn()
            macro_data.append({'Indicator': lbl, 'Value': val, 'Signal': cls, 'Detail': ''})
        except Exception:
            macro_data.append({'Indicator': lbl, 'Value': 'Error', 'Signal': '-', 'Detail': '-'})

    # Fetch all asset data
    print(f"Fetching data for {len(ASSETS)} assets...")
    asset_data = {}
    for name, ticker in ASSETS.items():
        try:
            print(f"  - {ticker}...")
            asset_data[name] = calculate_technicals(ticker)
        except Exception:
            asset_data[name] = None

    # Prepare asset analysis data
    asset_rows = []
    momentum_rows = []

    for name, ticker in ASSETS.items():
        tech = asset_data.get(name)
        if tech:
            # Asset analysis row
            price_fmt = f"${tech['price']:,.2f}" if tech['price'] > 1 else f"${tech['price']:.4f}"
            zscore_val = f"{tech['zscore']:+.2f}" if tech['zscore'] is not None else "N/A"
            tsmom_val = f"{tech['tsmom_score']:+.2f}%" if tech['tsmom_score'] is not None else "N/A"
            ma_val = f"{tech['ma_score']}/{tech['ma_max']}" if tech['ma_score'] is not None else "N/A"
            adx_val = f"{tech['adx']:.0f}" if tech['adx'] is not None else "N/A"

            asset_rows.append({
                'Asset': ticker,
                'Price': price_fmt,
                'Z-Score': zscore_val,
                'TSMOM': tsmom_val,
                'MA_Score': ma_val,
                'ADX': adx_val,
                'Regime': tech['regime'],
                'Regime_Bias': tech['regime_bias']
            })

            # Momentum details row
            if tech.get('tsmom_details'):
                details = tech['tsmom_details']
                ret_4w = details[0].split(': ')[1] if len(details) > 0 else "-"
                ret_12w = details[1].split(': ')[1] if len(details) > 1 else "-"
                ret_26w = details[2].split(': ')[1] if len(details) > 2 else "-"

                momentum_rows.append({
                    'Asset': ticker,
                    '4w_Return': ret_4w,
                    '12w_Return': ret_12w,
                    '26w_Return': ret_26w,
                    'MA_Distance': tech['ma_distance']
                })
        else:
            asset_rows.append({
                'Asset': ticker,
                'Price': 'Error',
                'Z-Score': '-',
                'TSMOM': '-',
                'MA_Score': '-',
                'ADX': '-',
                'Regime': '-',
                'Regime_Bias': '-'
            })

    # Write CSV files
    print("\nWriting CSV files...")

    # Macro indicators CSV
    macro_file = output_dir / f"macro_indicators_{timestamp}.csv"
    with open(macro_file, 'w', newline='', encoding='utf-8') as f:
        if macro_data:
            writer = csv.DictWriter(f, fieldnames=macro_data[0].keys())
            writer.writeheader()
            writer.writerows(macro_data)
    print(f"  - {macro_file}")

    # Asset analysis CSV
    asset_file = output_dir / f"asset_analysis_{timestamp}.csv"
    with open(asset_file, 'w', newline='', encoding='utf-8') as f:
        if asset_rows:
            writer = csv.DictWriter(f, fieldnames=asset_rows[0].keys())
            writer.writeheader()
            writer.writerows(asset_rows)
    print(f"  - {asset_file}")

    # Momentum details CSV
    momentum_file = output_dir / f"momentum_details_{timestamp}.csv"
    with open(momentum_file, 'w', newline='', encoding='utf-8') as f:
        if momentum_rows:
            writer = csv.DictWriter(f, fieldnames=momentum_rows[0].keys())
            writer.writeheader()
            writer.writerows(momentum_rows)
    print(f"  - {momentum_file}")

    print(f"\nAnalysis complete. Files saved to: {output_dir}")


if __name__ == "__main__":
    main()
