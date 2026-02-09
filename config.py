"""Configuration and constants for the trading analysis system."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Paths
SCRIPT_DIR = Path(__file__).parent
DEFAULT_ASSETS_FILE = SCRIPT_DIR / "assets.json"
CACHE_DIR = SCRIPT_DIR / ".cache"
OUTPUT_DIR = SCRIPT_DIR / "output"

# Create directories
CACHE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# API Keys
FRED_API_KEY = os.getenv("FRED_API_KEY")
if not FRED_API_KEY:
    raise ValueError("FRED_API_KEY environment variable is not set. Please check your .env file.")

# Technical Indicators
MA_PERIODS = [20, 50, 100, 200]

# Cache Settings
CACHE_MAX_AGE_DAYS = 7

# ADX Settings
# Daily: 14-period, Weekly: 21-period
ADX_DAILY_WINDOW = 14
ADX_WEEKLY_WINDOW = 21

# ADX Levels:
# < 20: No trend (use tanh mean-reversion signals)
# 20-25: Trend emerging
# 25-40: Trending (follow trend, don't fade)
# > 40: Strong trend (watch for reversal when declining)
ADX_NO_TREND = 20
ADX_TREND_EMERGING = 25
ADX_STRONG_TREND = 40

# TSMOM Settings
TSMOM_LOOKBACKS = [4, 12, 26]  # weeks

# RSI Settings
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

# Bollinger Bands Settings
BB_PERIOD = 20

# KAMA Settings (Kaufman's Adaptive Moving Average)
# Used as trend filter on daily timeframe
# window: Efficiency Ratio period
# pow1: Fast EMA constant (fastest smoothing)
# pow2: Slow EMA constant (slowest smoothing)
KAMA_WINDOW = 10  # ER period
KAMA_FAST = 2     # Fast EMA
KAMA_SLOW_DAILY = 30  # Slow EMA for daily
KAMA_SLOW_WEEKLY = 12  # Slow EMA for weekly (if needed later)

# GLI (Global Liquidity Index) FRED Series
GLI_SERIES = {
    # US Fed components (weekly)
    'fed_bs': 'WALCL',        # Fed total assets (millions USD)
    'tga': 'WTREGEN',         # Treasury General Account (millions USD)
    'rrp': 'RRPONTSYD',       # Reverse Repo (billions USD)
    # Global central banks
    'ecb_bs': 'ECBASSETSW',   # ECB assets (millions EUR, weekly)
    'boj_bs': 'JPNASSETS',    # BOJ assets (100 million JPY, monthly)
    # M2 Money Supply
    'usa_m2': 'M2SL',         # US M2 (billions USD, monthly)
    'eur_m2': 'MYAGM2EZM196N',# Eurozone M2 (EUR, monthly)
    'jpy_m2': 'MYAGM2JPM189S',# Japan M2 (JPY, monthly)
    'cny_m2': 'MYAGM2CNM189N',# China M2 (CNY, monthly)
    # FX rates for conversion
    'eurusd': 'DEXUSEU',      # USD per EUR
    'usdjpy': 'DEXJPUS',      # JPY per USD (invert for USD per JPY)
    'usdcny': 'DEXCHUS',      # CNY per USD (invert for USD per CNY)
}

