"""Caching utilities for market data."""

import json
import pickle
import time
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf

from config import CACHE_DIR, CACHE_MAX_AGE_DAYS


def get_cache_path(cache_key):
    """Get cache file path for today."""
    today = datetime.now().strftime('%Y%m%d')
    return CACHE_DIR / f"{cache_key}_{today}.json"


def load_from_cache(cache_key):
    """Load data from cache if exists and is from today."""
    cache_file = get_cache_path(cache_key)
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return None


def save_to_cache(cache_key, data):
    """Save data to cache with today's date."""
    cache_file = get_cache_path(cache_key)
    # Clean old cache files for this key
    for old_file in CACHE_DIR.glob(f"{cache_key}_*.json"):
        if old_file != cache_file:
            old_file.unlink()
    with open(cache_file, 'w') as f:
        json.dump(data, f)


def cleanup_orphan_caches(max_age_days=CACHE_MAX_AGE_DAYS):
    """Remove orphan cache files older than max_age_days."""
    cutoff_time = time.time() - (max_age_days * 86400)
    for cache_file in CACHE_DIR.glob("*_historical.pkl"):
        if cache_file.stat().st_mtime < cutoff_time:
            cache_file.unlink()


def get_cached_ticker(ticker, period, interval, fresh=False):
    """
    Smart persistent cache for yfinance data.
    Returns cached data if last bar is recent, otherwise fetches fresh data.

    Args:
        ticker: Stock ticker symbol
        period: Data period (e.g., '1y', '5y')
        interval: Data interval (e.g., '1d', '1wk')
        fresh: If True, skip cache and always fetch fresh data

    Best practices:
    - Uses auto_adjust=True for split/dividend adjusted prices
    - Handles timezone-aware datetimes properly
    - Validates data before caching
    """
    cache_file = CACHE_DIR / f"{ticker}_{interval}_historical.pkl"

    # Skip cache for fresh requests (important for daily data during market hours)
    if not fresh and cache_file.exists():
        try:
            cached_data = pd.read_pickle(cache_file)
            if not cached_data.empty and len(cached_data) > 0:
                # Convert timezone-aware to date for comparison
                last_date = cached_data.index[-1]
                if hasattr(last_date, 'date'):
                    last_date = last_date.date()
                else:
                    last_date = pd.Timestamp(last_date).date()

                # Only use cache if last bar is from today
                # This ensures fresh data is fetched when new trading day begins
                today = datetime.now().date()
                if last_date >= today:
                    return cached_data
        except (FileNotFoundError, EOFError, pd.errors.EmptyDataError, pickle.PickleError):
            pass

    # Fetch fresh data with best practices
    try:
        data = yf.download(
            ticker,
            period=period,
            interval=interval,
            auto_adjust=True,  # Adjust for splits/dividends
            progress=False,
            ignore_tz=False  # Preserve timezone info
        )

        # Handle MultiIndex columns (happens with single ticker sometimes)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Validate data before caching
        if not data.empty and len(data) > 0 and 'Close' in data.columns:
            data.to_pickle(cache_file)
            return data
        else:
            # Return empty DataFrame if download failed
            return pd.DataFrame()

    except Exception as e:
        print(f"Warning: Failed to download {ticker}: {e}")
        return pd.DataFrame()
