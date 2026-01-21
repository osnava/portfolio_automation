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

# ZTanh Settings
ZTANH_PERIODS = [20, 50, 100, 200]
