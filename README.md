# Quantitative Market Analysis Framework

**Version 4.0.0** - RSI + Bollinger Bands with standard settings

A systematic approach to multi-asset analysis combining macro liquidity metrics, volatility regime detection, and technical indicators across equities, cryptocurrencies, and commodities. Features smart caching, complete weekly candle handling, and LLM-enhanced commentary by OSCR (Quantitative Research Analyst).

## What's New in v4.0.0

- **RSI Indicator**: Standard 14-period RSI with 30/70 thresholds (replaces ZTanh)
- **Bollinger Bands**: 20-period with 1/2/3 standard deviation bands on Daily sheet
- **Simplified Configuration**: No more ticker-specific weights/thresholds files
- **VIX RSI**: Contrary indicator for market sentiment (high RSI = fear = buy opportunity)

## Methodology

- **Macro Liquidity Metrics**

  - Global Liquidity Index (GLI) - Net Fed liquidity after TGA and RRP adjustments
  - VIX volatility regime classification (Low/Normal/Elevated/High)
  - VIX RSI sentiment indicator for contrarian signals

- **Statistical Technical Analysis**

  **Weekly Timeframe (21-period ADX):**
  - **RSI** - 14-period Relative Strength Index (0-100)
  - Time-Series Momentum (TSMOM) - Average percentage return across 4w/12w/26w lookbacks
  - MA Score - 7-point moving average alignment indicator (20/50/100/200-period)
  - Regime Classification - Trending Up, Trending Down, Emerging Up/Down, Trend Unclear, Mean Revert Buy/Sell, Choppy, Neutral
  - Directional Movement Index (ADX) for trend strength quantification
  - Moving average distance metrics for trend confirmation

  **Daily Timeframe (14-period ADX):**
  - **RSI** - 14-period Relative Strength Index
  - **Bollinger Bands** - Position relative to 1/2/3 standard deviation bands
  - ADX with action recommendation (mean-reversion vs trend-following)
  - DI Bias - Directional Indicator bias (Bullish/Bearish/Neutral)
  - KAMA - Kaufman's Adaptive Moving Average as trend filter

  **Multi-Timeframe Decision Logic:**
  - Weekly determines **direction** (trend/regime identification)
  - Daily determines **timing** (entry/exit precision)
  - ADX < 20: Use RSI mean-reversion signals
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

## Configuration

All indicator settings are in `config.py`:

```python
# RSI Settings
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

# Bollinger Bands Settings
BB_PERIOD = 20

# ADX Settings
ADX_DAILY_WINDOW = 14
ADX_WEEKLY_WINDOW = 21
```

## Performance Optimizations

### Smart Persistent Caching

The system implements intelligent caching for maximum performance:

**Cache Strategy:**
- **First run each day**: Downloads fresh data from yfinance
- **Subsequent runs same day**: Uses cache (completes in <5 seconds)
- **Next trading day**: Automatically fetches new data

**Cache Location:** `.cache/` directory (gitignored)
- Weekly data: `TICKER_1wk_historical.pkl`
- Daily data: `TICKER_1d_historical.pkl`
- Macro data: JSON files with daily timestamps

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
- **Macro**: Data timeframes (weekly/daily candle dates), GLI, VIX, VIX RSI (with sentiment)
- **Weekly**: Asset signals with RSI, RSI_Zone, TSMOM, MA Score, ADX, Regime (complete weeks only)
- **Momentum**: Detailed 4w/12w/26w percentage returns with MA distances
- **Daily**: RSI, RSI_Zone, ADX with action recommendation, DI Bias, KAMA, BB_Position

**File format:** `output/YYYYMMDD_HHMM_ANALYSIS.xlsx` (e.g., `20260129_1617_ANALYSIS.xlsx`)

**Features:**
- Conditional formatting (color-coded cells: green=oversold, red=overbought)
- Auto-optimized column widths
- Numeric data types for Excel formulas
- Professional color scheme for quick visual analysis
- Adaptive formatting (automatically adjusts to any number of assets)

## Project Structure

**Version 4.0.0** - Modular architecture with RSI + Bollinger Bands

```
trading/
├── weekly_market_tracker.py    # Main entry point
├── config.py                    # Configuration & constants
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
│   ├── rsi_bb.py                # RSI and Bollinger Bands
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
│   └── SYSPROMPT.MD             # OSCR analysis instructions (v4.0.0)
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

- **Modular**: Clean separation of concerns
- **Maintainable**: Each module has single responsibility
- **Testable**: Components can be tested in isolation
- **Extensible**: Easy to add new indicators or strategies
- **Simple**: Standard indicator settings, no custom calibration needed

## Example Output

**Console output during execution:**
```
Fetching market data...
Date: Wednesday, 2026-01-29 14:30
Portfolio: tickers
Fetching GLI data...
Fetching VIX data...
Fetching data for 9 assets...
  - SPY (weekly + daily)...
  - BTC-USD (weekly + daily)...
  - GLD (weekly + daily)...
  - ETH-USD (weekly + daily)...

Writing XLSX file...
  - output/20260129_1430_tickers_ANALYSIS.xlsx

Applying conditional formatting...
  - Applied conditional formatting and optimized column widths
  - Formatting applied

Analysis complete. File saved to: output
```

**Generated XLSX file structure:**

### Sheet 1: Macro
| Indicator | Value | Unit | Signal | Detail |
|-----------|-------|------|--------|--------|
| Weekly Data (Complete Week) | 2026-01-26 | Date | Last Complete | All weekly indicators use this candle |
| Daily Data (Most Recent) | 2026-01-28 | Date | Latest Available | All daily indicators use this candle |
| Global Liquidity | 5777.45 | Billions USD | Expanding | 4w: +1.73% \| 12w: +0.52% |
| VIX | 17.23 | Index | Normal | - |
| VIX RSI | 45.2 | [0-100] | Neutral | - |

### Sheet 2: Weekly
| Name | Ticker | Price | RSI | RSI_Zone | TSMOM_% | MA_Score | MA_Max | ADX | Regime | Regime_Bias |
|------|--------|-------|-----|----------|---------|----------|--------|-----|--------|-------------|
| SMH | SMH | 389.22 | 62.5 | Neutral | +18.43 | 7 | 7 | 30 | Trending Up | Trend-following: long |
| BTC-USD | BTC-USD | 90427 | 48.3 | Neutral | +5.50 | 5 | 7 | 26 | Trend Unclear | Trend present, signals mixed |

### Sheet 3: Momentum
| Name | Ticker | 4w_Return_% | 12w_Return_% | 26w_Return_% | MA_Distance |
|------|--------|-------------|--------------|--------------|-------------|
| SMH | SMH | +12.5 | +20.8 | +22.0 | MA20: +3.2% \| MA50: +8.9% \| ... |

### Sheet 4: Daily
| Name | Ticker | Price | RSI | RSI_Zone | ADX | ADX_Action | DI_Bias | KAMA | KAMA_Dist% | Price_vs_KAMA | BB_Position |
|------|--------|-------|-----|----------|-----|------------|---------|------|------------|---------------|-------------|
| SMH | SMH | 389.22 | 58.3 | Neutral | 28.5 | Trend-follow | Bullish | 380.5 | +2.3 | Extended Above | Above +1 STD |

**Color coding:**
- Green: Oversold RSI (<30), Below BB bands, Positive TSMOM
- Red: Overbought RSI (>70), Above BB bands, Negative TSMOM
- White: Neutral values

## RSI Indicator

Standard 14-period Relative Strength Index:

| RSI | Zone | Interpretation |
|-----|------|----------------|
| > 70 | Overbought | Potential reversal down |
| 30-70 | Neutral | No extreme reading |
| < 30 | Oversold | Potential reversal up |

## Bollinger Bands

20-period moving average with bands at 1, 2, 3 standard deviations:

| Position | Interpretation |
|----------|----------------|
| Above +3 STD | Extreme overbought |
| Above +2 STD | Overbought |
| Above +1 STD | Above average |
| Within Bands | Normal range |
| Below -1 STD | Below average |
| Below -2 STD | Oversold |
| Below -3 STD | Extreme oversold |

## ADX Settings

| Timeframe | Period |
| --------- | ------ |
| Daily | 14 |
| Weekly | 21 |

**ADX Levels:**
| ADX | Interpretation | Action |
| --- | -------------- | ------ |
| < 20 | No trend | Use RSI mean-reversion signals |
| 20-25 | Trend emerging | Cautious trend-following |
| 25-40 | Trending | Follow trend, don't fade |
| > 40 | Strong trend | Watch for reversal when declining |

## LLM-Enhanced Signal Generation with OSCR

Augment quantitative signals with qualitative factor analysis by integrating XLSX output with large language models configured as **OSCR** (Quantitative Research Analyst):

1. Execute analysis routine to generate XLSX file
2. Upload XLSX file to LLM (Claude, ChatGPT, Gemini)
3. Configure LLM with system prompt from `prompts/SYSPROMPT.MD` (v4.0.0)
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

- **Regime Classification**: Trending Up | Trending Down | Emerging Up/Down | Trend Unclear | Mean Revert Buy/Sell | Choppy | Neutral
- **TSMOM_% (Momentum)**: >+15% Strong positive | +5% to +15% Moderate | +2% to +5% Weak | -2% to +2% Neutral | <-5% Negative
- **MA Score (Alignment)**: 7/7 Strong uptrend | 5-6/7 Uptrend | 3-4/7 Mixed | 0-2/7 Downtrend
- **ADX (Trend Strength)**: <20 No trend | 20-25 Emerging | 25-40 Trending | >40 Strong
- **RSI (Price Momentum)**: >70 Overbought | <30 Oversold
- **VIX Regime**: <15 Low | 15-20 Normal | 20-30 Elevated | >30 High
- **VIX RSI Sentiment**: Extreme Fear (>80) | Fear (70-80) | Mild Fear (60-70) | Neutral (40-60) | Mild Greed (30-40) | Greed (20-30) | Extreme Greed (<20)
- **Signals**: BUY | BUY THE DIP | WAIT | SELL THE TOP | SELL

## Technical Stack

- **yfinance** - Yahoo Finance market data API wrapper
- **pandas** - Time series data structures and analysis
- **numpy** - Vectorized numerical computation
- **ta** - Technical indicator library (RSI, Bollinger Bands, ADX, KAMA)
- **requests** - HTTP client for FRED API integration
- **python-dotenv** - Environment configuration management
- **openpyxl** - Excel file generation with conditional formatting and styling

## License

MIT License - Open source for research, personal, and commercial applications.
