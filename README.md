# Quantitative Market Analysis Framework

**Version 3.1.0** - Improved regime classification and simulator framing

A systematic approach to multi-asset analysis combining macro liquidity metrics, volatility regime detection, and statistical technical indicators across equities, cryptocurrencies, and commodities. Features smart caching, complete weekly candle handling, and LLM-enhanced commentary by OSCR (Quantitative Research Analyst).

## What's New in v3.0.0

- ✅ **ZTanh Indicator**: Learned z-score transformation with tanh activation [-1, +1]
- ✅ **Ticker-Specific Thresholds**: Custom thresholds for VIX, BTC-USD, and default assets
- ✅ **Updated ADX Settings**: Daily (14-period), Weekly (21-period) with new levels
- ✅ **Simplified Macro**: Removed VIX Z-Score, using simple VIX levels
- ✅ **Removed TEMA**: Replaced with MA Score and ZTanh for daily analysis
- ✅ **External Configuration**: weights.json and thresholds.json for easy tuning

## Methodology

- **Macro Liquidity Metrics**

  - Global Liquidity Index (GLI) - Net Fed liquidity after TGA and RRP adjustments
  - VIX volatility regime classification (Low/Normal/Elevated/High)
  - VIX ZTanh sentiment indicator for mean reversion signals

- **Statistical Technical Analysis**

  **Weekly Timeframe (21-period ADX):**
  - **ZTanh** - Learned z-score transformation with tanh activation, bounded [-1, +1]
  - Time-Series Momentum (TSMOM) - Average percentage return across 4w/12w/26w lookbacks
  - MA Score - 7-point moving average alignment indicator (20/50/100/200-period)
  - Regime Classification - TRENDING_UP, TRENDING_DOWN, TREND_EMERGING_UP/DOWN, TREND_UNCLEAR, MEAN_REVERT_BUY/SELL, CHOPPY, NEUTRAL
  - Directional Movement Index (ADX) for trend strength quantification
  - Moving average distance metrics for trend confirmation

  **Daily Timeframe (14-period ADX):**
  - **ZTanh** - Daily z-score transformation with ticker-specific thresholds
  - MA Score - 7-point moving average alignment (20/50/100/200-period)
  - MA Distance - Percentage distance from each moving average
  - ADX with action recommendation (mean-reversion vs trend-following)
  - DI Bias - Directional Indicator bias (Bullish/Bearish/Neutral)
  - Trend classification based on MA alignment and ADX

  **Multi-Timeframe Decision Logic:**
  - Weekly determines **direction** (trend/regime identification)
  - Daily determines **timing** (entry/exit precision)
  - ADX < 20: Use ZTanh mean-reversion signals
  - ADX > 25: Follow trend, don't fade

- **Universe Coverage**

  - Equity ETFs: ISAC.L (Global), SMH (Semiconductors), URA (Uranium), ROBO (Robotics), ARKQ (Autonomous Tech)
  - Individual Stocks: PLTR (Palantir)
  - Digital Assets: BTC-USD, ETH-USD, PAXG-USD (tokenized gold)
  - Benchmark Indices: SPY (S&P 500)
  - Precious Metals: GLD (Gold), SLV (Silver)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd trading
```

2. Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up your FRED API key:

   - Get a free API key from [FRED](https://fred.stlouisfed.org/docs/api/api_key.html)
   - Create a `.env` file in the project root:

   ```
   FRED_API_KEY=your_api_key_here
   ```

## Configuration Files

### weights.json
Contains the learned weights for ZTanh calculation:
```json
{
  "encoder_weight": [0.1149, 0.1121, 0.1249, 0.1093],
  "encoder_bias": -0.2184
}
```

### thresholds.json
Contains ticker-specific ZTanh thresholds for zone classification:
```json
{
  "^VIX": {
    "daily": { "extreme_ob": 0.85, "overbought": 0.70, ... },
    "weekly": { "extreme_ob": 0.85, "overbought": 0.67, ... }
  },
  "BTC-USD": {
    "daily": { ... },
    "weekly": { ... }
  },
  "default": {
    "daily": { ... },
    "weekly": { ... }
  }
}
```

## Performance Optimizations

### Smart Persistent Caching

The system implements intelligent caching for maximum performance:

**Cache Strategy:**
- **First run each day**: Downloads fresh data from yfinance (5-10 min for 12 assets)
- **Subsequent runs same day**: Uses cache (completes in <5 seconds)
- **Next trading day**: Automatically fetches new data

**Cache Location:** `.cache/` directory (gitignored)
- Weekly data: `TICKER_1wk_historical.pkl`
- Daily data: `TICKER_1d_historical.pkl`
- Macro data: JSON files with daily timestamps

**Benefits:**
- ✅ **120x faster** on repeat runs (30 min → 5 sec)
- ✅ **Bandwidth efficient**: Only downloads when needed
- ✅ **Always fresh**: Cache expires automatically each trading day
- ✅ **Run anytime**: Safe to run multiple times per day

### yfinance Best Practices

Following official yfinance documentation recommendations:

1. **Native Intervals**: Uses `interval="1wk"` for complete weekly candles only (no partial weeks)
2. **Auto-Adjust**: Automatically handles stock splits and dividends
3. **Timezone Handling**: Properly manages timezone-aware datetimes
4. **Error Handling**: Graceful fallbacks for missing data or API failures

**Weekly Data Guarantee:**
- Script uses **complete weekly candles only** (ending Sunday)
- Mid-week runs still use last complete Sunday candle (stable signals)
- Weekly indicators never use partial weeks

## Execution

Execute systematic analysis routine with default portfolio:

```bash
python weekly_market_tracker.py
```

Or specify a custom portfolio file:

```bash
python weekly_market_tracker.py tickers.json
```

**Output:** Generates a timestamped XLSX file with 4 sheets:
- **Macro**: Data timeframes (weekly/daily candle dates), GLI, VIX, VIX ZTanh (with sentiment)
- **Weekly**: Asset signals with ZTanh, ZTanh_Zone, TSMOM, MA Score, ADX, Regime (complete weeks only)
- **Momentum**: Detailed 4w/12w/26w percentage returns with MA distances
- **Daily**: ZTanh, ZTanh_Zone, MA Score, MA Distance, ADX with action recommendation, DI Bias, Trend

**File format:** `output/YYYYMMDD_HHMM_ANALYSIS.xlsx` (e.g., `20260119_1617_ANALYSIS.xlsx`)

**Features:**
- ✅ Conditional formatting (color-coded cells: green=positive, red=negative)
- ✅ Auto-optimized column widths
- ✅ Numeric data types for Excel formulas
- ✅ Professional color scheme for quick visual analysis
- ✅ Adaptive formatting (automatically adjusts to any number of assets)

## Project Structure

**Version 3.0.0** - Modular architecture with ZTanh indicator

```
trading/
├── weekly_market_tracker.py    # Main entry point
├── config.py                    # Configuration & constants
├── weights.json                 # ZTanh encoder weights
├── thresholds.json              # Ticker-specific ZTanh thresholds
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .env                         # API keys (create this)
├── .gitignore                   # Git exclusions
│
├── data/                        # Data layer
│   ├── __init__.py
│   ├── cache.py                 # Smart persistent caching
│   ├── fetchers.py              # API data fetchers (FRED, VIX)
│   └── loaders.py               # Asset loading
│
├── indicators/                  # Technical indicators
│   ├── __init__.py
│   ├── ztanh.py                 # ZTanh indicator with thresholds
│   ├── momentum.py              # TSMOM, MA score
│   └── trend.py                 # ADX, trend detection
│
├── analysis/                    # Analysis engines
│   ├── __init__.py
│   ├── regime.py                # Market regime classification
│   ├── weekly.py                # Weekly technical analysis
│   └── daily.py                 # Daily technical analysis
│
├── reporting/                   # Output generation
│   ├── __init__.py
│   ├── excel.py                 # Excel file generation
│   └── formatters.py            # Formatting utilities
│
├── prompts/                     # LLM configuration
│   └── SYSPROMPT.MD             # OSCR analysis instructions (v3.0.0)
│
├── tickers/                     # Portfolio definitions
│   ├── assets.json              # Default portfolio
│   └── ...                      # Custom portfolios
│
├── output/                      # Generated XLSX files (gitignored)
│   └── YYYYMMDD_HHMM_ANALYSIS.xlsx
│
└── .cache/                      # Persistent yfinance cache (gitignored)
    └── TICKER_INTERVAL_historical.pkl
```

### Architecture Benefits

- ✅ **Modular**: Clean separation of concerns
- ✅ **Maintainable**: Each module has single responsibility
- ✅ **Testable**: Components can be tested in isolation
- ✅ **Extensible**: Easy to add new indicators or strategies
- ✅ **Configurable**: External JSON files for weights and thresholds

## Example Output

**Console output during execution:**
```
Fetching market data...
Date: Sunday, 2026-01-19 14:30
Portfolio: tickers
Fetching GLI data...
Fetching VIX data...
Fetching data for 9 assets...
Fetching data for 5 assets...
  - SPY (weekly + daily)...
  - BTC-USD (weekly + daily)...
  - GLD (weekly + daily)...
  - ^VIX (weekly + daily)...
  - ETH-USD (weekly + daily)...

Writing XLSX file...
  - output/20260119_1430_tickers_ANALYSIS.xlsx

Applying conditional formatting...
  - Applied conditional formatting and optimized column widths
  - Formatting applied

Analysis complete. File saved to: output
```

**Generated XLSX file structure:**

### Sheet 1: Macro
| Indicator | Value | Unit | Signal | Detail |
|-----------|-------|------|--------|--------|
| Weekly Data (Complete Week) | 2026-01-12 | Date | Last Complete | All weekly indicators use this candle |
| Daily Data (Most Recent) | 2026-01-17 | Date | Latest Available | All daily indicators use this candle |
| Global Liquidity | 5777.45 | Billions USD | Expanding | 4w: +1.73% \| 12w: +0.52% |
| VIX | 17.23 | Index | Normal | - |
| VIX ZTanh | +0.15 | [-1, +1] | Neutral | - |

### Sheet 2: Weekly
| Name | Ticker | Price | ZTanh | ZTanh_Zone | TSMOM_% | MA_Score | MA_Max | ADX | Regime | Regime_Bias |
|------|--------|-------|-------|------------|---------|----------|--------|-----|--------|-------------|
| SMH | SMH | 389.22 | +0.72 | Upper | +18.43 | 7 | 7 | 30 | TRENDING_UP | Trend-following: long |
| BTC-USD | BTC-USD | 90427 | -0.35 | Lower | +5.50 | 5 | 7 | 26 | TREND_UNCLEAR | Trend present, signals mixed |

### Sheet 3: Momentum
| Name | Ticker | 4w_Return_% | 12w_Return_% | 26w_Return_% | MA_Distance |
|------|--------|-------------|--------------|--------------|-------------|
| SMH | SMH | +12.5 | +20.8 | +22.0 | MA20: +3.2% \| MA50: +8.9% \| ... |

### Sheet 4: Daily
| Name | Ticker | Price | ZTanh | ZTanh_Zone | MA_Score | MA_Dist | ADX | ADX_Action | DI_Bias | Trend |
|------|--------|-------|-------|------------|----------|---------|-----|------------|---------|-------|
| SMH | SMH | 389.22 | +0.55 | Upper | 7 | MA20: +0.9% \| ... | 28.5 | Follow trend | Bullish | Strong Bullish |

**Color coding:**
- 🟢 Green: Positive values (TSMOM >0%, returns >0%, MA Score high)
- 🔴 Red: Negative values (TSMOM <0%, returns <0%)
- 🟡 Yellow: Overbought ZTanh (>+0.70)
- ⚪ White: Neutral values (ZTanh near 0)

## ZTanh Indicator

The ZTanh indicator combines multiple z-scores using learned weights and tanh activation:

```
ZTanh = tanh(w1*Z_20 + w2*Z_50 + w3*Z_100 + w4*Z_200 + bias)
```

**Benefits:**
- Bounded output [-1, +1] for consistent interpretation
- Learned weights capture cross-period relationships
- Ticker-specific thresholds account for different volatility profiles

**Default Weekly Thresholds:**
| ZTanh | Zone |
| ----- | ---- |
| > 0.85 | Extreme OB |
| 0.75 - 0.85 | Overbought |
| 0.65 - 0.75 | Upper |
| -0.10 - 0.65 | Neutral |
| -0.40 - -0.10 | Lower |
| -0.60 - -0.40 | Oversold |
| < -0.60 | Extreme OS |

## ADX Settings

| Timeframe | Period |
| --------- | ------ |
| Daily | 14 |
| Weekly | 21 |

**ADX Levels:**
| ADX | Interpretation | Action |
| --- | -------------- | ------ |
| < 20 | No trend | Use ZTanh mean-reversion signals |
| 20-25 | Trend emerging | Cautious trend-following |
| 25-40 | Trending | Follow trend, don't fade |
| > 40 | Strong trend | Watch for reversal when declining |

## LLM-Enhanced Signal Generation with OSCR

Augment quantitative signals with qualitative factor analysis by integrating XLSX output with large language models configured as **OSCR** (Quantitative Research Analyst):

1. Execute analysis routine to generate XLSX file
2. Upload XLSX file to LLM (Claude, ChatGPT, Gemini)
3. Configure LLM with system prompt from `prompts/SYSPROMPT.MD` (v3.0.0)
4. Select risk profile: Conservative, Moderate, or Aggressive
5. **Enable extended reasoning mode** for optimal inference quality
6. LLM analyzes all 4 sheets as **OSCR** and generates:
   - **Data tables**: Mechanical signal classification (BUY/SELL/WAIT)
   - **OSCASH MARKETS Commentary**: Ultra-concise bullet-point analysis by OSCR

## Global Liquidity Index (GLI) Methodology

Quantifies net dollar liquidity circulating in financial markets via Federal Reserve system accounts.

**Calculation:** `GLI = Fed Balance Sheet - TGA - RRP`

### Components

| Term | FRED Code | Full Name | Description |
| ---- | --------- | --------- | ----------- |
| **Fed BS** | `WALCL` | Fed Total Assets | Total assets held by the Federal Reserve |
| **TGA** | `WTREGEN` | Treasury General Account | US Treasury's checking account at the Fed |
| **RRP** | `RRPONTSYD` | Reverse Repo | Cash parked at the Fed by money market funds |

### Signal Interpretation

- **Expanding** (+1% over 4-weeks): Net liquidity growth, positive for risk asset beta
- **Contracting** (-1% over 4-weeks): Liquidity withdrawal, risk-off regime likely

## Signal Interpretation Guide

- **Regime Classification**: TRENDING_UP | TRENDING_DOWN | TREND_EMERGING_UP/DOWN | TREND_UNCLEAR | MEAN_REVERT_BUY/SELL | CHOPPY | NEUTRAL
- **TSMOM_% (Momentum)**: >+15% Strong positive | +5% to +15% Moderate | +2% to +5% Weak | -2% to +2% Neutral | <-5% Negative
- **MA Score (Alignment)**: 7/7 Strong uptrend | 5-6/7 Uptrend | 3-4/7 Mixed | 0-2/7 Downtrend
- **ADX (Trend Strength)**: <20 No trend | 20-25 Emerging | 25-40 Trending | >40 Strong
- **ZTanh (Price Deviation)**: >+0.75 Overbought | <-0.50 Oversold (varies by ticker)
- **VIX Regime**: <15 Low | 15-20 Normal | 20-30 Elevated | >30 High
- **VIX ZTanh Sentiment**: Extreme Fear (<-0.70) | Fear (-0.70 to -0.50) | Mild Fear (-0.50 to -0.20) | Neutral (-0.20 to +0.20) | Mild Greed (+0.20 to +0.50) | Greed (+0.50 to +0.70) | Extreme Greed (>+0.70)
- **Signals**: BUY | BUY THE DIP | WAIT | SELL THE TOP | SELL

## Technical Stack

- **yfinance** - Yahoo Finance market data API wrapper
- **pandas** - Time series data structures and analysis
- **numpy** - Vectorized numerical computation
- **ta** - Technical indicator library (ADX, moving averages)
- **requests** - HTTP client for FRED API integration
- **python-dotenv** - Environment configuration management
- **yfinance** - VIX data for sentiment analysis
- **openpyxl** - Excel file generation with conditional formatting and styling

## License

MIT License - Open source for research, personal, and commercial applications.
