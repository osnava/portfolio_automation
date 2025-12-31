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
from ta.momentum import StochRSIIndicator
from ta.trend import MACD, ADXIndicator

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
    "ISAC": "ISAC.L",
    "SMH": "SMH",
    "URA": "URA",
    "ROBO": "ROBO",
    "ARKQ": "ARKQ",
    "BTCUSD": "BTC-USD",
    "ETHUSD": "ETH-USD",
    "SPX": "^GSPC",
    "GOLD": "GC=F",
    "SILVER": "SI=F",
}

MA_PERIODS = [20, 50, 100, 200]

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

def interpret_stoch_rsi(k, d):
    """Interpret Stoch RSI (0-1 scale from ta library)."""
    if k is None or np.isnan(k):
        return "N/A"
    
    k = round(k * 100, 1)
    d = round(d * 100, 1) if d and not np.isnan(d) else None
    
    zone = "Overbought" if k > 80 else "Oversold" if k < 20 else \
           "Upper Neutral" if k > 60 else "Lower Neutral" if k < 40 else "Neutral"
    
    cross = " ^" if d and k > d and abs(k - d) < 10 else " v" if d and k < d and abs(k - d) < 10 else ""
    return f"{zone} ({k}){cross}"


def interpret_macd(macd_val, hist, hist_prev=None):
    """Interpret MACD values."""
    if macd_val is None or np.isnan(macd_val):
        return "N/A"
    
    trend = "Bullish" if hist > 0 else "Bearish"
    
    momentum = ""
    if hist_prev is not None and not np.isnan(hist_prev):
        strengthening = (hist > 0 and hist > hist_prev) or (hist < 0 and hist < hist_prev)
        momentum = " Strengthening" if strengthening else " Weakening"
    
    cross = " [Near Cross]" if abs(hist) < abs(macd_val) * 0.1 else ""
    return f"{trend}{momentum}{cross}"


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
    
    strength = "Moderate" if adx < 40 else "Strong"
    threshold = 3 if adx < 40 else 2
    
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
        stoch = StochRSIIndicator(close_col, window=14, smooth1=3, smooth2=3)
        macd = MACD(close_col)
        hist = macd.macd_diff()
        return {
            'stoch_rsi': interpret_stoch_rsi(stoch.stochrsi_k().iloc[-1], stoch.stochrsi_d().iloc[-1]),
            'macd': interpret_macd(macd.macd().iloc[-1], hist.iloc[-1], hist.iloc[-2] if len(hist) > 1 else None),
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
        weekly = {'stoch_rsi': 'N/A', 'macd': 'N/A', 'ma_distance': 'N/A', 'trend': 'Insufficient Data', 'trend_strength': 'N/A', 'adx': None}
    
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
    
    print("\n  Volatility:")
    try:
        if vix := get_vix():
            desc = "Low" if vix < 15 else "Normal" if vix < 20 else "Elevated" if vix < 30 else "High"
            print(f"     VIX: {vix} - {desc}")
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
                    print(f"     RSI: {d['stoch_rsi']} | MACD: {d['macd']}")
                    print(f"     MAs: {d['ma_distance']}")
            else:
                print("  ❌ Could not retrieve")
        except Exception:
            print("  ❌ Could not retrieve")
    
    # LEGEND
    print(f"\n{'='*90}\n  📖 QUICK REFERENCE\n{'='*90}")
    print("  TREND: 📈 Up | 📉 Down | ↔️ Sideways | ADX: <20 Weak, 20-40 Mod, >40 Strong")
    print("  RSI: >80 OB | <20 OS | ^ Bull cross | v Bear cross")
    print("  MACD: Bull/Bear + Strength/Weak | [Near Cross] = reversal")
    print("  F&G: 0-25 Ext Fear | 26-45 Fear | 46-55 Neutral | 56-75 Greed | 76-100 Ext Greed")
    print("  GLI: 📈 Expanding >1% | 📉 Contracting <-1% | ➡️ Flat")
    print("=" * 90)
    print()


if __name__ == "__main__":
    main()
