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
ZSCORE_WINDOW = 20

# Cache Settings
CACHE_MAX_AGE_DAYS = 7

# TEMA Ensemble Settings
# Base period sets (fast, mid, slow)
TEMA_BASE_PERIODS = [
    (15, 40, 150),   # Fast: Catches early moves, more whipsaws
    (20, 50, 200),   # Standard: Industry standard
    (30, 75, 250),   # Slow: Filters noise, lags entries
]

# ADX Settings
ADX_WINDOW = 14
ADX_CHOPPY_THRESHOLD = 20
ADX_MODERATE_THRESHOLD = 25

# TSMOM Settings
TSMOM_LOOKBACKS = [4, 12, 26]  # weeks

# Volatility Settings
VOLATILITY_LOOKBACK = 252  # days
VOLATILITY_ATR_PERIOD = 14
VOLATILITY_SCALAR_MIN = 0.5
VOLATILITY_SCALAR_MAX = 2.0

# VIX Settings
VIX_ZSCORE_WINDOW = 252  # 1 year of trading days
VIX_ZSCORE_EMA_SPAN = 5
