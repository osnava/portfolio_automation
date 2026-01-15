#!/usr/bin/env python3
"""Weekly Market Analysis Tracker - Main Entry Point"""

import sys
import warnings
from datetime import datetime
from pathlib import Path

import pandas as pd

# Configuration and utilities
from config import OUTPUT_DIR
from data.loaders import load_assets
from data.cache import cleanup_orphan_caches
from data.fetchers import (
    calculate_gli,
    get_vix_zscore,
    get_fear_greed_traditional,
    get_fear_greed_crypto,
    get_regime_from_vix_z
)
from analysis.weekly import calculate_technicals
from analysis.daily import calculate_daily_technicals
from reporting.excel import apply_conditional_formatting
from reporting.formatters import format_sign

warnings.filterwarnings('ignore')


def main():
    # Parse command line argument for assets file
    assets_file = sys.argv[1] if len(sys.argv) > 1 else None
    ASSETS = load_assets(assets_file)

    # Get assets file name for display
    assets_name = Path(assets_file).stem if assets_file else "assets"

    # Generate timestamp-based filename (24-hour format, no seconds)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')

    print(f"Fetching market data...")
    print(f"Date: {datetime.now().strftime('%A, %Y-%m-%d %H:%M')}")

    # Cleanup old orphan caches
    cleanup_orphan_caches(max_age_days=7)
    print(f"Portfolio: {assets_name}")

    # Collect macro data
    macro_data = []

    # GLI
    print("Fetching GLI data...")
    try:
        if gli := calculate_gli():
            macro_data.append({
                'Indicator': 'Global Liquidity',
                'Value': round(gli['value'], 2),
                'Unit': 'Billions USD',
                'Signal': gli['trend'],
                'Detail': f"4w: {format_sign(gli['mom_pct'])}% | 12w: {format_sign(gli['qoq_pct'])}%"
            })
        else:
            macro_data.append({'Indicator': 'Global Liquidity', 'Value': None, 'Unit': None, 'Signal': 'Error', 'Detail': 'Error'})
    except Exception:
        macro_data.append({'Indicator': 'Global Liquidity', 'Value': None, 'Unit': None, 'Signal': 'Error', 'Detail': 'Error'})

    # VIX
    print("Fetching VIX data...")
    try:
        vix, vix_z = get_vix_zscore()
        if vix:
            vix_levels = [(15, "Low"), (20, "Normal"), (30, "Elevated"), (float('inf'), "High")]
            vix_desc = next(desc for threshold, desc in vix_levels if vix < threshold)
            regime = get_regime_from_vix_z(vix_z)
            macro_data.append({'Indicator': 'VIX', 'Value': round(vix, 2), 'Unit': 'Index', 'Signal': vix_desc, 'Detail': ''})
            macro_data.append({'Indicator': '-Z(VIX)', 'Value': round(vix_z, 2), 'Unit': 'Z-Score', 'Signal': regime, 'Detail': ''})
    except Exception:
        macro_data.append({'Indicator': 'VIX', 'Value': None, 'Unit': None, 'Signal': 'Error', 'Detail': 'Error'})

    # Fear & Greed
    print("Fetching Fear & Greed indices...")
    for fn, lbl in [(get_fear_greed_traditional, 'F&G Stocks'), (get_fear_greed_crypto, 'F&G Crypto')]:
        try:
            val, cls = fn()
            macro_data.append({'Indicator': lbl, 'Value': int(val), 'Unit': '0-100 Scale', 'Signal': cls, 'Detail': ''})
        except Exception:
            macro_data.append({'Indicator': lbl, 'Value': None, 'Unit': None, 'Signal': 'Error', 'Detail': 'Error'})

    # Fetch all asset data (weekly and daily)
    print(f"Fetching data for {len(ASSETS)} assets...")
    asset_data = {}
    daily_data = {}
    for name, ticker in ASSETS.items():
        try:
            print(f"  - {ticker} (weekly + daily)...")
            asset_data[name] = calculate_technicals(ticker)
            daily_data[name] = calculate_daily_technicals(ticker)
        except Exception as e:
            print(f"    ERROR: {e}")
            asset_data[name] = None
            daily_data[name] = None

    # Extract dates from first available ticker data
    weekly_candle_date = None
    daily_candle_date = None
    for name in ASSETS.keys():
        if asset_data.get(name) and asset_data[name].get('weekly_date'):
            weekly_candle_date = asset_data[name]['weekly_date']
            break
    for name in ASSETS.keys():
        if daily_data.get(name) and daily_data[name].get('daily_date'):
            daily_candle_date = daily_data[name]['daily_date']
            break

    # Add data timeframe info to macro section
    if weekly_candle_date:
        macro_data.insert(0, {
            'Indicator': 'Weekly Data (Complete Week)',
            'Value': weekly_candle_date,
            'Unit': 'Date',
            'Signal': 'Last Complete',
            'Detail': 'All weekly indicators use this candle'
        })
    if daily_candle_date:
        macro_data.insert(1 if weekly_candle_date else 0, {
            'Indicator': 'Daily Data (Most Recent)',
            'Value': daily_candle_date,
            'Unit': 'Date',
            'Signal': 'Latest Available',
            'Detail': 'All daily indicators use this candle'
        })

    # Prepare asset analysis data
    asset_rows = []
    momentum_rows = []
    daily_rows = []

    for name, ticker in ASSETS.items():
        tech = asset_data.get(name)
        if tech:
            # Asset analysis row - use numeric types for Excel
            asset_rows.append({
                'Name': name,
                'Ticker': ticker,
                'Price': round(tech['price'], 4),
                'Z-Score': round(tech['zscore'], 2) if tech['zscore'] is not None else None,
                'TSMOM_%': round(tech['tsmom_score'], 2) if tech['tsmom_score'] is not None else None,
                'MA_Score': tech['ma_score'] if tech['ma_score'] is not None else None,
                'MA_Max': tech['ma_max'] if tech['ma_max'] is not None else None,
                'ADX': round(tech['adx'], 1) if tech['adx'] is not None else None,
                'Regime': tech['regime'],
                'Regime_Bias': tech['regime_bias']
            })

            # Momentum details row - extract numeric values
            if tech.get('tsmom_details'):
                details = tech['tsmom_details']
                # Parse "4w: +2.5%" -> 2.5
                ret_4w = float(details[0].split(': ')[1].rstrip('%')) if len(details) > 0 else None
                ret_12w = float(details[1].split(': ')[1].rstrip('%')) if len(details) > 1 else None
                ret_26w = float(details[2].split(': ')[1].rstrip('%')) if len(details) > 2 else None

                momentum_rows.append({
                    'Name': name,
                    'Ticker': ticker,
                    '4w_Return_%': ret_4w,
                    '12w_Return_%': ret_12w,
                    '26w_Return_%': ret_26w,
                    'MA_Distance': tech['ma_distance']  # Keep as text (complex format)
                })
        else:
            asset_rows.append({
                'Name': name,
                'Ticker': ticker,
                'Price': None,
                'Z-Score': None,
                'TSMOM_%': None,
                'MA_Score': None,
                'MA_Max': None,
                'ADX': None,
                'Regime': 'Error',
                'Regime_Bias': 'Error'
            })

        # Daily technicals row - use numeric types for Excel
        daily_tech = daily_data.get(name)
        if daily_tech:
            # Consolidate TEMA distances into one readable string
            tema_dist = f"20:{daily_tech['tema20_dist']:+.1f}% | 50:{daily_tech['tema50_dist']:+.1f}% | 200:{daily_tech['tema200_dist']:+.1f}%"

            # Consolidate crosses into one column
            crosses = []
            if daily_tech['cross_20_50'] != 'None':
                crosses.append(f"20x50:{daily_tech['cross_20_50'].replace(' Cross', '')}")
            if daily_tech['cross_50_200'] != 'None':
                crosses.append(f"50x200:{daily_tech['cross_50_200'].replace(' Cross', '')}")
            crosses_str = " | ".join(crosses) if crosses else "None"

            daily_rows.append({
                'Name': name,
                'Ticker': ticker,
                'Price': round(daily_tech['price'], 4),
                'Z-Score': round(daily_tech['zscore_daily'], 2) if daily_tech['zscore_daily'] is not None else None,
                'TEMA_Dist': tema_dist,
                'Crosses': crosses_str,
                'ADX': round(daily_tech['adx_daily'], 1),
                'Consensus': round(daily_tech['tema_consensus'], 2),
                'Confidence': round(daily_tech['tema_confidence'], 2),
                'Ensemble': daily_tech['tema_ensemble'],
                'Trend': daily_tech['trend_ensemble'],
                'Vol_Scalar': round(daily_tech['vol_scalar'], 2),
            })
        else:
            daily_rows.append({
                'Name': name,
                'Ticker': ticker,
                'Price': None,
                'Z-Score': None,
                'TEMA_Dist': 'Error',
                'Crosses': 'Error',
                'ADX': None,
                'Consensus': None,
                'Confidence': None,
                'Ensemble': 'Error',
                'Trend': 'Error',
                'Vol_Scalar': None,
            })

    # Write XLSX file with multiple sheets
    print("\nWriting XLSX file...")

    xlsx_file = OUTPUT_DIR / f"{timestamp}_ANALYSIS.xlsx"

    with pd.ExcelWriter(xlsx_file, engine='openpyxl') as writer:
        # Sheet 1: Macro indicators
        if macro_data:
            df_macro = pd.DataFrame(macro_data)
            df_macro.to_excel(writer, sheet_name='Macro', index=False)

        # Sheet 2: Weekly signals
        if asset_rows:
            df_weekly = pd.DataFrame(asset_rows)
            df_weekly.to_excel(writer, sheet_name='Weekly', index=False)

        # Sheet 3: Momentum details
        if momentum_rows:
            df_momentum = pd.DataFrame(momentum_rows)
            df_momentum.to_excel(writer, sheet_name='Momentum', index=False)

        # Sheet 4: Daily signals
        if daily_rows:
            df_daily = pd.DataFrame(daily_rows)
            df_daily.to_excel(writer, sheet_name='Daily', index=False)

    print(f"  - {xlsx_file}")

    # Apply conditional formatting
    print("\nApplying conditional formatting...")
    apply_conditional_formatting(xlsx_file, len(asset_rows))
    print("  - Formatting applied")

    print(f"\nAnalysis complete. File saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
