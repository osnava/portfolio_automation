#!/usr/bin/env python3
"""Weekly Market Analysis Tracker"""

import os
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv
from ta.trend import ADXIndicator

warnings.filterwarnings('ignore')

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

FRED_API_KEY = os.getenv("FRED_API_KEY")
if not FRED_API_KEY:
    raise ValueError("FRED_API_KEY environment variable is not set. Please check your .env file.")

ASSETS = {
    "iShares MSCI ACWI ETF": "ISAC.L",
    "VanEck Semiconductor ETF": "SMH",
    "Global X Uranium ETF": "URA",
    "ROBO Global Robotics and Automation ETF": "ROBO",
    "ARK Autonomous Technology & Robotics ETF": "ARKQ",
    "Bitcoin USD": "BTC-USD",
    "Ethereum USD": "ETH-USD",
    "S&P 500": "^GSPC",
    "Gold Futures": "GC=F",
    "Silver Futures": "SI=F",
}

MA_PERIODS = [20, 50, 200]
ZSCORE_WINDOW = 20

# ============================================================================
# DATA FETCHING
# ============================================================================

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


def get_vix():
    """Fetch current VIX value."""
    hist = yf.Ticker("^VIX").history(period="5d")
    return round(hist['Close'].iloc[-1], 2) if not hist.empty else None


def get_vix_zscore():
    """Fetch VIX and calculate smoothed inverted Z-score (52-day window, 5-period EMA)."""
    hist = yf.download("^VIX", period="3mo", interval="1d", progress=False)
    if hist.empty or len(hist) < 52:
        return None, None

    if isinstance(hist.columns, pd.MultiIndex):
        hist.columns = hist.columns.get_level_values(0)

    vix_series = hist['Close']
    vix = round(vix_series.iloc[-1], 2)

    # Z-score with 52-day window
    mean = vix_series.rolling(52).mean()
    std = vix_series.rolling(52).std()
    z = (vix_series - mean) / std

    # Invert and smooth with 5-period EMA
    z_inverted = -z
    z_smooth = z_inverted.ewm(span=5, adjust=False).mean()

    return vix, round(z_smooth.iloc[-1], 2)


# ============================================================================
# GLI CALCULATION
# ============================================================================

def calculate_gli():
    """Calculate Global Liquidity Index: Fed Balance Sheet - TGA - RRP."""
    fed_data = get_fred_series("WALCL", limit=14)
    tga_data = get_fred_series("WTREGEN", limit=14)
    rrp_data = get_fred_series("RRPONTSYD", limit=70)
    
    if not all([fed_data, tga_data, rrp_data]):
        return None
    
    tga_by_date = {d: v for v, d in tga_data}
    
    gli_series = []
    for fed_val, fed_date in fed_data:
        tga_val = tga_by_date.get(fed_date)
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


# ============================================================================
# TECHNICAL ANALYSIS
# ============================================================================

def calculate_zscore(close, window=ZSCORE_WINDOW):
    """Calculate z-score for price series."""
    if len(close) < window:
        return None, None

    mean = close.rolling(window).mean().iloc[-1]
    std = close.rolling(window).std().iloc[-1]

    if std == 0 or np.isnan(std):
        return 0, "Neutral"

    zscore = (close.iloc[-1] - mean) / std
    zscore = round(zscore, 2)

    if zscore >= 2.5:
        zone = "Extreme OB"
    elif zscore >= 2:
        zone = "Overbought"
    elif zscore >= 1:
        zone = "Upper"
    elif zscore <= -2.5:
        zone = "Extreme OS"
    elif zscore <= -2:
        zone = "Oversold"
    elif zscore <= -1:
        zone = "Lower"
    else:
        zone = "Neutral"

    return zscore, zone


def format_ma_distance(close, price, periods):
    """Calculate distance from MAs."""
    parts = []
    for p in periods:
        if len(close) >= p:
            ma = close.rolling(p).mean().iloc[-1]
            pct = ((price - ma) / ma) * 100
            parts.append(f"MA{p}: {abs(pct):.1f}%{'↑' if pct > 0 else '↓'}")
    return " | ".join(parts) or "N/A"


def detect_trend(df):
    """Detect trend using MAs, ADX, and directional indicators."""
    if len(df) < 50:
        return "Insufficient Data", "N/A", None
    
    close, high, low = df['Close'], df['High'], df['Low']
    price = close.iloc[-1]
    
    ma20 = close.rolling(20).mean().iloc[-1]
    ma50 = close.rolling(50).mean().iloc[-1]
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
    if ma200 is not None:
        score += (1 if price > ma200 else -1) + (1 if ma50 > ma200 else -1)
    
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
    """Calculate all technical indicators for an asset."""
    data = yf.download(ticker, period="1y", interval="1d", progress=False)
    if data.empty:
        return None

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    close = data['Close']

    def get_indicators(df, close_col):
        zscore, zone = calculate_zscore(close_col)
        return {
            'zscore': zscore,
            'zscore_zone': zone,
            'ma_distance': format_ma_distance(close_col, close_col.iloc[-1], MA_PERIODS),
        }

    daily = get_indicators(data, close)
    daily['trend'], daily['trend_strength'], daily['adx'] = detect_trend(data)

    weekly_df = data.resample('W').agg({
        'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
    }).dropna()

    if len(weekly_df) >= 26:
        weekly = get_indicators(weekly_df, weekly_df['Close'])
        weekly['trend'], weekly['trend_strength'], weekly['adx'] = detect_trend(weekly_df) if len(weekly_df) >= 50 else ("Insufficient Data", "N/A", None)
    else:
        weekly = {'zscore': None, 'zscore_zone': 'N/A', 'ma_distance': 'N/A', 'trend': 'Insufficient Data', 'trend_strength': 'N/A', 'adx': None}

    return {'price': close.iloc[-1], 'daily': daily, 'weekly': weekly}


# ============================================================================
# MAIN
# ============================================================================


def main():
    print(f"\n{'='*90}\n  📊 WEEKLY MARKET ANALYSIS - {datetime.now().strftime('%A, %Y-%m-%d %H:%M')}\n{'='*90}")
    
    # MACRO
    print("\n  🌍 MACRO INDICATORS\n  " + "─" * 50)
    
    print("\n  Global Liquidity Index:")
    try:
        if gli := calculate_gli():
            print(f"     Net Liquidity:  ${gli['value']}B  {gli['trend']}")
            print(f"     Fed: ${gli['fed_bs']}B | TGA: ${gli['tga']}B | RRP: ${gli['rrp']}B | Date: {gli['date']}")
            for lbl, chg, pct in [("WoW", gli['wow_change'], gli['wow_pct']),
                                   ("4-Week", gli['mom_change'], gli['mom_pct']),
                                   ("12-Week", gli['qoq_change'], gli['qoq_pct'])]:
                if pct is not None:
                    print(f"     {lbl}: {'+' if chg >= 0 else ''}${chg}B ({'+' if chg >= 0 else ''}{pct}%)")
        else:
            print("     ❌ Could not retrieve")
    except Exception:
        print("     ❌ Could not retrieve")
    
    print("\n  Volatility & Regime:")
    try:
        vix, vix_z = get_vix_zscore()
        if vix:
            vix_desc = "Low" if vix < 15 else "Normal" if vix < 20 else "Elevated" if vix < 30 else "High"
            if vix_z >= 1.5:
                regime = "Complacency"
            elif vix_z <= -1.5:
                regime = "Fear"
            elif vix_z >= 0.5:
                regime = "Risk-On"
            elif vix_z <= -0.5:
                regime = "Risk-Off"
            else:
                regime = "Neutral"
            print(f"     VIX: {vix} ({vix_desc})")
            print(f"     -Z(VIX): {vix_z:+.2f} → {regime}")
        else:
            print("     ❌ Could not retrieve")
    except Exception:
        print("     ❌ Could not retrieve")
    
    print("\n  Sentiment:")
    for fn, lbl in [(get_fear_greed_traditional, 'Stocks'), (get_fear_greed_crypto, 'Crypto')]:
        try:
            val, cls = fn()
            print(f"     Fear & Greed ({lbl}): {val} - {cls}")
        except Exception:
            print(f"     Fear & Greed ({lbl}): ❌ Could not retrieve")
    
    # ASSETS
    print(f"\n{'='*90}\n  📈 ASSET ANALYSIS\n{'='*90}")
    
    for name, ticker in ASSETS.items():
        print(f"\n{'─'*90}\n  {name} ({ticker})\n{'─'*90}")
        
        try:
            if tech := calculate_technicals(ticker):
                print(f"\n  💰 ${tech['price']:,.2f}" if tech['price'] > 1 else f"\n  💰 ${tech['price']:.6f}")
                for tf, icon in [('daily', '📅'), ('weekly', '📆')]:
                    d = tech[tf]
                    print(f"\n  {icon} {tf.upper()}: {d['trend']} ({d['trend_strength']}, ADX: {d['adx']})")
                    z_display = f"{d['zscore']:+.2f}" if d['zscore'] is not None else "N/A"
                    print(f"     Z-Score: {z_display} ({d['zscore_zone']})")
                    print(f"     MAs: {d['ma_distance']}")
            else:
                print("  ❌ Could not retrieve")
        except Exception:
            print("  ❌ Could not retrieve")
    
    # LEGEND
    print(f"\n{'='*90}\n  📖 QUICK REFERENCE\n{'='*90}")
    print("  TREND: 📈 Up | 📉 Down | ↔️ Sideways | ADX: <20 Weak, 20-25 Mod, >25 Strong")
    print("  Z-SCORE: >+2 OB | <-2 OS | >+2.5 Extreme OB | <-2.5 Extreme OS")
    print("  -Z(VIX): >+1.5 Complacency | <-1.5 Fear | ±0.5-1.5 Risk-On/Off")
    print("  F&G: 0-25 Ext Fear | 26-45 Fear | 46-55 Neutral | 56-75 Greed | 76-100 Ext Greed")
    print("  GLI: 📈 Expanding >1% | 📉 Contracting <-1% | ➡️ Flat")
    print("=" * 90)
    print()


if __name__ == "__main__":
    main()
