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
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

warnings.filterwarnings('ignore')
console = Console()

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
        console.print(f"[red]Error: Assets file not found: {file_path}[/red]")
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
    """Fetch VIX and calculate smoothed inverted Z-score (52-day rolling window, 5-period EMA)."""
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


# GLI CALCULATION

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


# TECHNICAL ANALYSIS

def calculate_tsmom(close, lookbacks=[4, 12, 26]):
    """
    Time-series momentum for long-only: score 0-1
    1.0 = all lookbacks positive, 0.0 = all negative
    """
    if len(close) < max(lookbacks):
        return None, []

    scores = []
    details = []
    for lb in lookbacks:
        ret = (close.iloc[-1] / close.iloc[-lb] - 1) * 100
        is_positive = ret > 0
        scores.append(1 if is_positive else 0)
        details.append(f"{lb}w: {ret:+.1f}%")

    composite = sum(scores) / len(scores)
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
    """
    if adx is None or tsmom_score is None:
        return "UNKNOWN", "Insufficient data"

    ma_pct = (ma_score / ma_max) if ma_max > 0 else 0

    # Strong uptrend: high ADX + positive momentum + good MA alignment
    if adx > 25 and tsmom_score >= 0.67 and ma_pct >= 0.6:
        return "TRENDING_UP", "Ride trend, buy dips"

    # Strong downtrend: high ADX + negative momentum
    if adx > 25 and tsmom_score <= 0.33:
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

def get_regime_style(regime):
    """Return color style based on regime."""
    styles = {
        "TRENDING_UP": "bold green",
        "TRENDING_DOWN": "bold red",
        "MEAN_REVERT_BUY": "cyan",
        "MEAN_REVERT_SELL": "yellow",
        "CHOPPY": "dim",
        "NEUTRAL": "white",
        "UNKNOWN": "dim red",
    }
    return styles.get(regime, "white")


def get_tsmom_style(score):
    """Return color style based on TSMOM score."""
    if score is None:
        return "dim"
    if score >= 0.67:
        return "green"
    if score <= 0.33:
        return "red"
    return "yellow"


def get_zscore_style(zscore):
    """Return color style based on Z-score."""
    if zscore is None:
        return "dim"
    if zscore >= 2.0:
        return "bold red"
    if zscore <= -2.0:
        return "bold green"
    if zscore >= 1.5:
        return "red"
    if zscore <= -1.5:
        return "green"
    return "white"


def main():
    # Parse command line argument for assets file
    assets_file = sys.argv[1] if len(sys.argv) > 1 else None
    ASSETS = load_assets(assets_file)

    # Get assets file name for display
    assets_name = Path(assets_file).stem if assets_file else "assets"

    # Header
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]WEEKLY MARKET ANALYSIS[/bold cyan]\n[dim]{datetime.now().strftime('%A, %Y-%m-%d %H:%M')}[/dim]\n[dim cyan]Portfolio: {assets_name}[/dim cyan]",
        border_style="cyan"
    ))

    # MACRO TABLE
    macro_table = Table(title="MACRO INDICATORS", box=box.ROUNDED, border_style="blue")
    macro_table.add_column("Indicator", style="cyan", width=20)
    macro_table.add_column("Value", justify="right", width=15)
    macro_table.add_column("Signal", justify="center", width=15)
    macro_table.add_column("Detail", style="dim", width=35)

    # GLI
    try:
        if gli := calculate_gli():
            trend_style = "green" if "Expanding" in gli['trend'] else "red" if "Contracting" in gli['trend'] else "yellow"
            macro_table.add_row(
                "Global Liquidity",
                f"${gli['value']:,.0f}B",
                f"[{trend_style}]{gli['trend']}[/{trend_style}]",
                f"4w: {format_sign(gli['mom_pct'])}% | 12w: {format_sign(gli['qoq_pct'])}%"
            )
        else:
            macro_table.add_row("Global Liquidity", "[red]Error[/red]", "-", "-")
    except Exception:
        macro_table.add_row("Global Liquidity", "[red]Error[/red]", "-", "-")

    # VIX
    try:
        vix, vix_z = get_vix_zscore()
        if vix:
            vix_levels = [(15, "Low"), (20, "Normal"), (30, "Elevated"), (float('inf'), "High")]
            vix_desc = next(desc for threshold, desc in vix_levels if vix < threshold)
            vix_style = "green" if vix < 15 else "yellow" if vix < 25 else "red"
            regime = get_regime_from_vix_z(vix_z)
            regime_style = "green" if regime == "Fear" else "red" if regime == "Complacency" else "white"
            macro_table.add_row("VIX", f"[{vix_style}]{vix}[/{vix_style}]", vix_desc, "")
            macro_table.add_row("-Z(VIX)", f"{vix_z:+.2f}", f"[{regime_style}]{regime}[/{regime_style}]", "")
    except Exception:
        macro_table.add_row("VIX", "[red]Error[/red]", "-", "-")

    # Fear & Greed
    for fn, lbl in [(get_fear_greed_traditional, 'F&G Stocks'), (get_fear_greed_crypto, 'F&G Crypto')]:
        try:
            val, cls = fn()
            fg_style = "green" if val < 25 else "red" if val > 75 else "yellow" if val < 45 or val > 55 else "white"
            macro_table.add_row(lbl, f"[{fg_style}]{val}[/{fg_style}]", cls, "")
        except Exception:
            macro_table.add_row(lbl, "[red]Error[/red]", "-", "-")

    console.print()
    console.print(macro_table)

    # Fetch all asset data once
    console.print("\n[dim]Fetching asset data...[/dim]")
    asset_data = {}
    for name, ticker in ASSETS.items():
        try:
            asset_data[name] = calculate_technicals(ticker)
        except Exception:
            asset_data[name] = None

    # ASSETS TABLE
    asset_table = Table(title="ASSET ANALYSIS", box=box.ROUNDED, border_style="green")
    asset_table.add_column("Asset", style="bold", width=12, no_wrap=True)
    asset_table.add_column("Price", justify="right", width=11)
    asset_table.add_column("Z", justify="center", width=7)
    asset_table.add_column("TSMOM", justify="center", width=6)
    asset_table.add_column("MA", justify="center", width=5)
    asset_table.add_column("ADX", justify="center", width=4)
    asset_table.add_column("Regime", justify="left", width=18)

    for name, ticker in ASSETS.items():
        tech = asset_data.get(name)
        if tech:
            # Price
            price_fmt = f"${tech['price']:,.2f}" if tech['price'] > 1 else f"${tech['price']:.4f}"

            # Z-Score
            if tech['zscore'] is not None:
                z_style = get_zscore_style(tech['zscore'])
                z_display = f"[{z_style}]{tech['zscore']:+.2f}[/{z_style}]"
            else:
                z_display = "[dim]N/A[/dim]"

            # TSMOM
            if tech['tsmom_score'] is not None:
                t_style = get_tsmom_style(tech['tsmom_score'])
                tsmom_display = f"[{t_style}]{tech['tsmom_score']:.2f}[/{t_style}]"
            else:
                tsmom_display = "[dim]N/A[/dim]"

            # MA Score
            if tech['ma_score'] is not None:
                ma_pct = tech['ma_score'] / tech['ma_max']
                ma_style = "green" if ma_pct >= 0.7 else "red" if ma_pct <= 0.4 else "yellow"
                ma_display = f"[{ma_style}]{tech['ma_score']}/{tech['ma_max']}[/{ma_style}]"
            else:
                ma_display = "[dim]N/A[/dim]"

            # ADX
            if tech['adx'] is not None:
                adx_style = "green" if tech['adx'] > 25 else "yellow" if tech['adx'] > 20 else "dim"
                adx_display = f"[{adx_style}]{tech['adx']:.0f}[/{adx_style}]"
            else:
                adx_display = "[dim]N/A[/dim]"

            # Regime
            regime_style = get_regime_style(tech['regime'])
            regime_display = f"[{regime_style}]{tech['regime']}[/{regime_style}]"

            asset_table.add_row(
                ticker,
                price_fmt,
                z_display,
                tsmom_display,
                ma_display,
                adx_display,
                regime_display
            )
        else:
            asset_table.add_row(ticker, "[red]Error[/red]", "-", "-", "-", "-", "-")

    console.print()
    console.print(asset_table)

    # MOMENTUM DETAILS TABLE
    momentum_table = Table(title="MOMENTUM DETAILS", box=box.SIMPLE, border_style="dim")
    momentum_table.add_column("Asset", style="bold", width=16, no_wrap=True)
    momentum_table.add_column("4w", justify="right", width=9)
    momentum_table.add_column("12w", justify="right", width=9)
    momentum_table.add_column("26w", justify="right", width=9)
    momentum_table.add_column("MA Distance", width=50)

    for name, ticker in ASSETS.items():
        tech = asset_data.get(name)
        if tech and tech.get('tsmom_details'):
            details = tech['tsmom_details']
            ret_4w = details[0].split(': ')[1] if len(details) > 0 else "-"
            ret_12w = details[1].split(': ')[1] if len(details) > 1 else "-"
            ret_26w = details[2].split(': ')[1] if len(details) > 2 else "-"

            r4_style = "green" if ret_4w.startswith('+') else "red"
            r12_style = "green" if ret_12w.startswith('+') else "red"
            r26_style = "green" if ret_26w.startswith('+') else "red"

            momentum_table.add_row(
                ticker,
                f"[{r4_style}]{ret_4w}[/{r4_style}]",
                f"[{r12_style}]{ret_12w}[/{r12_style}]",
                f"[{r26_style}]{ret_26w}[/{r26_style}]",
                f"[dim]{tech['ma_distance']}[/dim]"
            )

    console.print()
    console.print(momentum_table)

    # Get macro regimes for summary
    gli_status = ""
    gli_warning = ""
    try:
        gli = calculate_gli()
        if gli:
            gli_trend = gli['trend']
            gli_4w = gli['mom_pct']
            gli_status = f"GLI {gli_trend} ({gli_4w:+.1f}% 4w)"
            if gli_4w and gli_4w <= -2:
                gli_warning = "[bold red]⚠ GLI CONTRACTING >2%: Downgrade all BUY→WAIT[/bold red]"
            elif gli_4w and gli_4w >= 2:
                gli_warning = "[bold green]✓ GLI EXPANDING: Risk-on favored[/bold green]"
    except:
        gli_status = "GLI: Unknown"

    vix_status = ""
    vix_warning = ""
    try:
        _, vix_z = get_vix_zscore()
        vix_regime = get_regime_from_vix_z(vix_z) if vix_z else "Unknown"
        vix_status = f"-Z(VIX) = {vix_z:+.2f} → {vix_regime}"
        if vix_z and vix_z >= 1.5:
            vix_warning = "[bold red]⚠ COMPLACENCY: Downgrade BUY→WAIT, upgrade SELL→STRONG SELL[/bold red]"
        elif vix_z and vix_z <= -1.5:
            vix_warning = "[bold green]✓ FEAR: Allow STRONG BUY on oversold assets[/bold green]"
    except:
        vix_status = "-Z(VIX): Unknown"

    # Combine warnings
    warnings = "\n".join(filter(None, [gli_warning, vix_warning]))
    if warnings:
        warnings = "\n" + warnings

    # LEGEND
    legend = f"""[bold cyan]MACRO REGIME[/bold cyan]
{gli_status} | {vix_status}{warnings}

[bold cyan]REFERENCE[/bold cyan]
[green]Z-Score:[/green] >+2 OB | <-2 OS | >+2.5 Extreme OB | <-2.5 Extreme OS
[green]TSMOM:[/green] 1.0=All↑ | 0.67=Mostly↑ | 0.33=Mostly↓ | 0.0=All↓
[green]MA Score:[/green] 7/7=Strong↑ | 5-6=↑ | 3-4=Mixed | 0-2=↓
[green]ADX:[/green] <20=Weak | 20-25=Mod | >25=Strong
[green]Regime:[/green] [bold green]TRENDING_UP[/bold green] | [bold red]TRENDING_DOWN[/bold red] | [cyan]MEAN_REVERT[/cyan] | [dim]CHOPPY[/dim]"""

    console.print()
    console.print(Panel(legend, border_style="dim"))
    console.print()


if __name__ == "__main__":
    main()
