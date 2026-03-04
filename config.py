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
}

# Broad money (M2/M3) series for GLI calculation
# Each entry: (FRED series, FX rate series, fx_mode, label)
#   fx_mode='multiply': val * fx_rate = USD (for DEXUSEU-style: USD per foreign)
#   fx_mode='divide':   val / fx_rate = USD (for DEXJPUS-style: foreign per USD)
#   fx_mode=None:       already in billions USD (no conversion needed)
# All non-USD series are in national currency units from FRED.
# Converted to billions USD, then summed.
GLI_BROAD_MONEY = {
    'usa':  {'series': 'M2SL',             'fx': None,      'fx_mode': None,       'scale': 1},
    'eur':  {'series': 'MABMM301EZM189N',  'fx': 'DEXUSEU', 'fx_mode': 'multiply', 'scale': 1e-9},
    'jpn':  {'series': 'MABMM301JPM189S',  'fx': 'DEXJPUS', 'fx_mode': 'divide',   'scale': 1e-9},
    'chn':  {'series': 'MYAGM2CNM189N',    'fx': 'DEXCHUS', 'fx_mode': 'divide',   'scale': 1e-9},
    'gbr':  {'series': 'MABMM301GBM189N',  'fx': 'DEXUSUK', 'fx_mode': 'multiply', 'scale': 1e-9},
    'can':  {'series': 'MABMM301CAM189N',  'fx': 'DEXCAUS', 'fx_mode': 'divide',   'scale': 1e-9},
    'aus':  {'series': 'MABMM301AUM189N',  'fx': 'DEXUSAL', 'fx_mode': 'multiply', 'scale': 1e-9},
    'ind':  {'series': 'MABMM301INM189N',  'fx': 'DEXINUS', 'fx_mode': 'divide',   'scale': 1e-9},
    'che':  {'series': 'MABMM301CHM189N',  'fx': 'DEXSZUS', 'fx_mode': 'divide',   'scale': 1e-9},
    'bra':  {'series': 'MABMM301BRM189N',  'fx': 'DEXBZUS', 'fx_mode': 'divide',   'scale': 1e-9},
    'kor':  {'series': 'MABMM301KRM189S',  'fx': 'DEXKOUS', 'fx_mode': 'divide',   'scale': 1e-9},
    'mex':  {'series': 'MABMM301MXM189N',  'fx': 'DEXMXUS', 'fx_mode': 'divide',   'scale': 1e-9},
}

# FX rates needed for GLI (superset of all FX used by CB balance sheets + broad money)
GLI_FX_RATES = {
    'DEXUSEU': 'multiply',  # USD per EUR
    'DEXJPUS': 'divide',    # JPY per USD
    'DEXCHUS': 'divide',    # CNY per USD
    'DEXUSUK': 'multiply',  # USD per GBP
    'DEXCAUS': 'divide',    # CAD per USD
    'DEXUSAL': 'multiply',  # USD per AUD
    'DEXINUS': 'divide',    # INR per USD
    'DEXSZUS': 'divide',    # CHF per USD
    'DEXBZUS': 'divide',    # BRL per USD
    'DEXKOUS': 'divide',    # KRW per USD
    'DEXMXUS': 'divide',    # MXN per USD
}

