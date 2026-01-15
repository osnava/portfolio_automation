# Quantitative Market Analysis Framework

**Version 2.8.0** - Modular architecture with OSCR intelligence

A systematic approach to multi-asset analysis combining macro liquidity metrics, volatility regime detection, and statistical technical indicators across equities, cryptocurrencies, and commodities. Features smart caching, complete weekly candle handling, and LLM-enhanced commentary by OSCR (Quantitative Research Analyst).

## What's New in v2.8.0

- ✅ **Modular Architecture**: 78% less code in main file (1,226 → 267 lines)
- ✅ **OSCR Persona**: PhD-level systematic market commentary
- ✅ **Smart Caching**: 120x faster on repeat runs (30 min → 5 sec)
- ✅ **Complete Weekly Candles**: Never uses partial weeks (mid-week safe)
- ✅ **Date Tracking**: Shows exact weekly/daily candle dates in Macro sheet
- ✅ **TEMA Ensemble**: Volatility-adaptive multi-period consensus
- ✅ **Ultra-Concise Commentary**: Bullet-point format (100-150 words)
- ✅ **yfinance Best Practices**: Auto-adjust, timezone handling, error recovery

## Methodology

- **Macro Liquidity Metrics**

  - Global Liquidity Index (GLI) - Net Fed liquidity after TGA and RRP adjustments
  - VIX volatility regime classification via normalized Z-Score transformation
  - Sentiment indicators (Fear & Greed indices) for mean reversion signals
- **Statistical Technical Analysis**

  **Weekly Timeframe:**
  - Time-Series Momentum (TSMOM) - Average percentage return across 4w/12w/26w lookbacks
  - MA Score - 7-point moving average alignment indicator (20/50/100/200-period)
  - Regime Classification - TRENDING_UP, TRENDING_DOWN, MEAN_REVERT, CHOPPY, NEUTRAL
  - Directional Movement Index (ADX) for trend strength quantification
  - Rolling Z-Score (20-period) for statistical overbought/oversold levels
  - Moving average distance metrics for trend confirmation

  **Daily Timeframe:**
  - TEMA (Triple Exponential Moving Average) - Fast-response MA for cross detection
  - **TEMA Ensemble** - Multi-period consensus (fast/standard/slow) with volatility adjustment
  - **Consensus** (-1.0 to +1.0) - Signal strength across period sets
  - **Confidence** (0.0 to 1.0) - Agreement level (1.0 = unanimous, 0.67 = majority)
  - Daily Z-Score (20-period) for near-term entry/exit timing
  - TEMA cross detection (20/50, 50/200) for trend change signals
  - Daily ADX for intraday trend strength
  - **Volatility Scalar** - Adaptive period adjustment based on ATR

  **Multi-Timeframe Decision Logic:**
  - Weekly determines **direction** (trend/regime identification)
  - Daily determines **timing** (entry/exit precision)
  - Example: Weekly BUY + Daily Bullish TEMA Cross = STRONG BUY (highest conviction)

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
python weekly_market_tracker.py tickers/assets_jorge.json
```

**Output:** Generates a timestamped XLSX file with 4 sheets:
- **Macro**: Data timeframes (weekly/daily candle dates), GLI, VIX, -Z(VIX), Fear & Greed indices
- **Weekly**: Asset signals with TSMOM, Z-Score, MA Score, ADX, Regime (complete weeks only)
- **Momentum**: Detailed 4w/12w/26w percentage returns with MA distances
- **Daily**: TEMA ensemble analysis with Consensus, Confidence, volatility-adaptive periods

**File format:** `output/YYYYMMDD_HHMM_ANALYSIS.xlsx` (e.g., `20260110_1617_ANALYSIS.xlsx`)

**Features:**
- ✅ Conditional formatting (color-coded cells: green=positive, red=negative)
- ✅ Auto-optimized column widths
- ✅ Numeric data types for Excel formulas
- ✅ Professional color scheme for quick visual analysis
- ✅ Adaptive formatting (automatically adjusts to any number of assets)

## Project Structure

**Version 2.8.0** - Modular architecture with clean separation of concerns

```
trading/
├── weekly_market_tracker.py    # Main entry point (267 lines)
├── config.py                    # Configuration & constants
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .env                         # API keys (create this)
├── .gitignore                   # Git exclusions
│
├── data/                        # Data layer
│   ├── __init__.py
│   ├── cache.py                 # Smart persistent caching
│   ├── fetchers.py              # API data fetchers (FRED, F&G, VIX)
│   └── loaders.py               # Asset loading
│
├── indicators/                  # Technical indicators
│   ├── __init__.py
│   ├── zscore.py                # Z-score calculations
│   ├── tema.py                  # TEMA & volatility-adaptive ensemble
│   ├── momentum.py              # TSMOM, MA score
│   └── trend.py                 # ADX, trend detection
│
├── analysis/                    # Analysis engines
│   ├── __init__.py
│   ├── regime.py                # Market regime classification
│   ├── weekly.py                # Weekly technical analysis
│   └── daily.py                 # Daily TEMA ensemble analysis
│
├── reporting/                   # Output generation
│   ├── __init__.py
│   ├── excel.py                 # Excel file generation
│   └── formatters.py            # Formatting utilities
│
├── prompts/                     # LLM configuration
│   └── SYSPROMPT.MD             # OSCR analysis instructions (v2.8.0)
│
├── tickers/                     # Portfolio definitions
│   ├── assets.json              # Default portfolio (12 assets)
│   ├── assets_jorge.json        # Extended portfolio (73 assets)
│   └── assets_mag7.json         # Magnificent 7 tech stocks
│
├── output/                      # Generated XLSX files (gitignored)
│   └── YYYYMMDD_HHMM_ANALYSIS.xlsx
│
├── .cache/                      # Persistent yfinance cache (gitignored)
│   └── TICKER_INTERVAL_historical.pkl
│
└── QF_TERMINOLOGY.md            # Complete terminology reference
```

### Architecture Benefits

- ✅ **Modular**: 78% less code in main file (1,226 → 267 lines)
- ✅ **Maintainable**: Each module has single responsibility
- ✅ **Testable**: Components can be tested in isolation
- ✅ **Extensible**: Easy to add new indicators or strategies
- ✅ **Reusable**: Modules can be imported by other scripts

### Portfolio Customization

Configure universe constituents via JSON files (supports all Yahoo Finance tickers).

**Default portfolio** (`assets.json`):

```json
{
  "iShares MSCI ACWI ETF": "ISAC.L",
  "VanEck Semiconductor ETF": "SMH",
  "Global X Uranium ETF": "URA",
  "ROBO Global Robotics and Automation ETF": "ROBO",
  "ARK Autonomous Technology & Robotics ETF": "ARKQ",
  "Palantir Technologies Inc.": "PLTR",
  "Bitcoin USD": "BTC-USD",
  "Ethereum USD": "ETH-USD",
  "SPDR S&P 500 ETF Trust": "SPY",
  "SPDR Gold Shares": "GLD",
  "iShares Silver Trust": "SLV",
  "PAX Gold USD": "PAXG-USD"
}
```

**Magnificent 7 portfolio** (`assets_mag7.json`):

```json
{
  "Apple Inc.": "AAPL",
  "Microsoft Corp.": "MSFT",
  "Amazon.com Inc.": "AMZN",
  "Alphabet Inc.": "GOOGL",
  "Meta Platforms Inc.": "META",
  "NVIDIA Corp.": "NVDA",
  "Tesla Inc.": "TSLA"
}
```

Create your own portfolio by adding a new JSON file following the same format.

**Ticker convention reference:**

- US Equities: Direct symbol notation (`AAPL`, `TSLA`)
- International Equities: Exchange-suffixed format (`ISAC.L` for LSE, `7203.T` for TSE)
- Digital Assets: USD pair notation (`BTC-USD`, `SOL-USD`)
- Benchmark Indices: Caret prefix (`^GSPC`, `^DJI`, `^IXIC`)
- Futures Contracts: Continuous contract notation (`GC=F`, `CL=F`)

## Example Output

**Console output during execution:**
```
Fetching market data...
Date: Saturday, 2026-01-10 19:06
Portfolio: assets_jorge
Fetching GLI data...
Fetching VIX data...
Fetching Fear & Greed indices...
Fetching data for 73 assets...
  - NVDA (weekly + daily)...
  - TSMC (weekly + daily)...
  - ASML (weekly + daily)...
  ...
  - RKLB (weekly + daily)...

Writing XLSX file...
  - output/20260110_1906_ANALYSIS.xlsx

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
| Daily Data (Most Recent) | 2026-01-15 | Date | Latest Available | All daily indicators use this candle |
| Global Liquidity | 5777.45 | Billions USD | Expanding | 4w: +1.73% \| 12w: +0.52% |
| VIX | 17.23 | Index | Normal | - |
| -Z(VIX) | +0.45 | Z-Score | Neutral | - |
| F&G Stocks | 48 | 0-100 Scale | Neutral | - |
| F&G Crypto | 52 | 0-100 Scale | Neutral | - |

### Sheet 2: Weekly
| Asset | Price | Z-Score | TSMOM_% | MA_Score | MA_Max | ADX | Regime | Regime_Bias |
|-------|-------|---------|---------|----------|--------|-----|--------|-------------|
| SMH | 389.22 | +1.84 | +18.43 | 7 | 7 | 30 | TRENDING_UP | Ride trend, buy dips |
| URA | 50.31 | +1.24 | +15.33 | 7 | 7 | 30 | TRENDING_UP | Ride trend, buy dips |
| BTC-USD | 90427.41 | -0.97 | -13.96 | 5 | 7 | 26 | TRENDING_DOWN | Avoid or exit |

### Sheet 3: Momentum
| Asset | 4w_Return_% | 12w_Return_% | 26w_Return_% | MA_Distance |
|-------|-------------|--------------|--------------|-------------|
| SMH | +12.5 | +20.8 | +22.0 | MA20: +3.2% \| MA50: +8.9% \| ... |
| URA | +8.9 | +18.2 | +19.9 | MA20: +2.1% \| MA50: +6.7% \| ... |

### Sheet 4: Daily
| Asset | Price | Z-Score | TEMA_Dist | Crosses | ADX | Consensus | Confidence | Ensemble | Trend | Vol_Scalar |
|-------|-------|---------|-----------|---------|-----|-----------|------------|----------|-------|------------|
| SMH | 389.22 | +1.45 | 20:+0.9% \| 50:+4.5% \| 200:+30.5% | None | 28.5 | +1.0 | 1.0 | 3/3 | Strong Bullish | 1.15 |
| URA | 50.31 | +0.89 | 20:+0.9% \| 50:+6.5% \| 200:+21.1% | 20x50:Bullish | 31.2 | +0.67 | 0.67 | 2/3 | Bullish | 1.05 |

**Color coding:**
- 🟢 Green: Positive values (TSMOM >0%, returns >0%, Consensus >0, Confidence high)
- 🔴 Red: Negative values (TSMOM <0%, returns <0%, Consensus <0)
- 🟡 Yellow: Overbought Z-scores (+2.0 and above)
- ⚪ White: Neutral values (Z-score -1 to +1, Consensus near 0)

## LLM-Enhanced Signal Generation with OSCR

Augment quantitative signals with qualitative factor analysis by integrating XLSX output with large language models configured as **OSCR** (Quantitative Research Analyst):

1. Execute analysis routine to generate XLSX file
2. Upload XLSX file to LLM (Claude, ChatGPT, Gemini)
3. Configure LLM with system prompt from `prompts/SYSPROMPT.MD` (v2.8.0)
4. Select risk profile: 🥛 Conservative, 📊 Moderate, or 🌶️ Aggressive
5. **Enable extended reasoning mode** for optimal inference quality (Claude "thinking", ChatGPT "o1", Gemini "thinking")
6. LLM analyzes all 4 sheets as **OSCR** and generates:
   - **Data tables**: Mechanical signal classification (BUY/SELL/WAIT)
   - **OSCASH MARKETS Commentary**: Ultra-concise bullet-point analysis by OSCR
   - PhD-level systematic approach with balanced tone (data first, selective opinions)
   - Format: REGIME → THESIS → CONVICTION PLAYS → EXITS → WATCHLIST → ACTIONS

### Recommended Models (as of Dec 2025)

**Proprietary Models (API-based):**

- **Claude Opus 4.5** (`claude-opus-4-5-20251124`) - Most intelligent, best reasoning
- **Claude Sonnet 4.5** (`claude-sonnet-4-5-20250929`) - Best for complex agents and coding
- **GPT-5** (`gpt-5`) - OpenAI's latest with unified reasoning
- **Gemini 2.0** (`gemini-2.0-flash-thinking-exp`) - Google's latest with thinking mode

**Open-Source Models (Self-hosted):**

- **DeepSeek R1** - 236B params, top open-source for logic & reasoning
- **Qwen 2.5 72B** - Excellent for research tasks, multilingual, strong reasoning
- **Llama 3.3 70B** - Meta's latest, clean controllable output
- **Mistral Large 2** - 123B params, near-GPT-4 performance, efficient

### Sample OSCR Commentary Output

Representative LLM-generated analysis using `prompts/SYSPROMPT.MD` (v2.8.0) - MODERATE profile:

**Table 1: Macro Summary**

| Indicator  | Value               | Signal     | Implication                                    |
| ---------- | ------------------- | ---------- | ---------------------------------------------- |
| GLI        | $5803B (+3.65% 4wk) | Expanding  | Liquidity injection favors risk-on positioning |
| VIX        | 15.27               | Normal     | Low implied vol, favorable hedge cost          |
| -Z(VIX)    | +0.90               | Risk-On    | Bullish environment, tight stops               |
| Stock F&G  | 51                  | Neutral    | No contrarian conviction signal                |
| Crypto F&G | 42                  | Fear       | Moderate fear, opportunity watch               |

**Table 2: Ticker Signals**

| Ticker | Price   | Z-Score | TSMOM_% | Regime           | Signal      | Key Drivers                                        |
| ------ | ------- | ------- | ------- | ---------------- | ----------- | -------------------------------------------------- |
| SMH    | $389.22 | +1.84   | +18.43  | TRENDING_UP      | WAIT        | Overbought Z +1.84, strong momentum but extended   |
| URA    | $50.31  | +1.24   | +15.33  | TRENDING_UP      | BUY         | Strong trend + TSMOM +15.33% + MA 7/7 + ADX 30    |
| GC=F   | $4490   | +1.50   | +15.30  | TRENDING_UP      | BUY         | Gold uptrend, strong momentum, ADX 64 very strong  |
| BTC    | $90,427 | -0.97   | -13.96  | TRENDING_DOWN    | WAIT        | Negative momentum -13.96%, wait for reversal      |
| PLTR   | $177.49 | +0.12   | +1.18   | NEUTRAL          | WAIT        | TSMOM +1.18% below threshold (+5%), no clear edge |

**Table 3: Rebalance Actions**

| Action | From | To     | Rationale                                                    |
| ------ | ---- | ------ | ------------------------------------------------------------ |
| BUY    | Cash | URA    | BUY: Strong uptrend + TSMOM +15.33% + MA 7/7 + ADX 30       |
| BUY    | Cash | GC=F   | BUY: Gold trending up + TSMOM +15.30% + very strong ADX 64  |
| TRIM   | SMH  | Cash   | Trim 25-50%: Overbought Z +1.84, lock profits on extension  |
| WAIT   | -    | BTC    | WAIT: Negative momentum -13.96%, await reversal confirmation |
| WAIT   | -    | PLTR   | WAIT: TSMOM +1.18% below +5% threshold, no clear edge       |

**OSCASH MARKETS Commentary (by OSCR):**

```
## OSCASH MARKETS - Jan 15, 2026 | MODERATE

**REGIME**
• GLI: $5,803B (expanding +3.7%) | VIX: 15.3 | -Z(VIX): +0.9 (Risk-On)
• Market: Risk-On with expanding liquidity

**THESIS**
Liquidity surge favors momentum continuation—GLI +3.7% supports risk assets, but watch overbought levels.

**CONVICTION PLAYS**
• URA: BUY | TSMOM +15.3%, Z +1.2, ADX 30, Conf 1.0 → Uranium uptrend intact → Size: 100%
• GLD: BUY | TSMOM +15.3%, Z +1.5, ADX 64, Conf 0.67 → Strong gold trend, high ADX → Size: 75%

**EXITS/TRIMS**
• SMH: SELL THE TOP | Z +1.8, TSMOM +18.4%—semiconductors extended despite momentum

**WATCHLIST** (Weekly signal ✓, Daily timing pending)
• No setups pending timing

**ACTIONS**
• BUY URA 100% position (Conf 1.0)—perfect trend alignment, MA 7/7
• BUY GLD 75% position (Conf 0.67)—ADX 64 very strong, accept majority confidence
• TRIM SMH 25-50%—Z +1.8 overbought, lock gains
• WAIT BTC—TSMOM -14.0%, downtrend persists

**BOTTOM LINE**
Strong liquidity backdrop supports selective longs, but trim overbought winners.

---
*Technical analysis only. Not investment advice. DYOR.*
```

## Global Liquidity Index (GLI) Methodology

Quantifies net dollar liquidity circulating in financial markets via Federal Reserve system accounts.

**Calculation:** `GLI = Fed Balance Sheet - TGA - RRP`

### Components

| Term             | FRED Code     | Full Name                | Description                                  |
| ---------------- | ------------- | ------------------------ | -------------------------------------------- |
| **Fed BS** | `WALCL`     | Fed Total Assets         | Total assets held by the Federal Reserve     |
| **TGA**    | `WTREGEN`   | Treasury General Account | US Treasury's checking account at the Fed    |
| **RRP**    | `RRPONTSYD` | Reverse Repo             | Cash parked at the Fed by money market funds |

### Liquidity Accounting Framework

```
Fed Balance Sheet    = Gross liquidity injection (QE programs)
- TGA                = Funds sequestered in Treasury account (non-circulating)
- RRP                = Overnight sterilization facility (non-circulating)
────────────────────────────────────────────────────────────────────
= Net Liquidity      = Available liquidity in financial system
```

### Component Price Impact

| Component  | Marginal Change           | Directional Effect                  |
| ---------- | ------------------------- | ----------------------------------- |
| **Fed BS** | QE / asset purchases      | Positive (liquidity injection)      |
| **TGA**    | Treasury cash accumulation | Negative (liquidity drain)          |
| **RRP**    | Excess reserve parking    | Negative (sterilizes bank reserves) |

### Signal Interpretation

- **Expanding** (+1% over 4-weeks): Net liquidity growth, positive for risk asset beta
- **Contracting** (-1% over 4-weeks): Liquidity withdrawal, risk-off regime likely
- **Empirical correlation**: GLI exhibits positive correlation with BTC, equities, and risk proxies

## Signal Interpretation Guide

- **Regime Classification**: TRENDING_UP | TRENDING_DOWN | MEAN_REVERT_BUY/SELL | CHOPPY | NEUTRAL
- **TSMOM_% (Momentum)**: >+15% Strong positive | +5% to +15% Moderate | +2% to +5% Weak | -2% to +2% Neutral/choppy | <-5% Negative
- **MA Score (Alignment)**: 7/7 Strong uptrend | 5-6/7 Uptrend | 3-4/7 Mixed | 0-2/7 Downtrend
- **ADX (Trend Strength)**: <20 Weak | 20-25 Moderate | >25 Strong | >40 Very strong
- **Z-Score (Price Deviation)**: >+2 Statistical OB | <-2 Statistical OS | >+2.5 Extreme | <-2.5 Extreme
- **-Z(VIX) Regime**: >+1.5 Complacency | <-1.5 Elevated fear | +/-0.5-1.5 Transitional
- **Sentiment Index**: 0-25 Extreme Fear | 26-45 Fear | 46-55 Neutral | 56-75 Greed | 76-100 Extreme Greed
- **GLI Trend**: Expanding >+1% | Contracting <-1% | Neutral
- **TEMA Alignment**: 3/3 Perfect bullish | 2/3 Moderate bullish | 1/3 Mixed | 0/3 Bearish
- **TEMA Crosses**: Bullish Cross (fast > slow) | Bearish Cross (fast < slow) | None
- **TEMA Consensus**: +1.0 Strong bullish | +0.67 Moderate bullish | 0.0 Mixed | -0.67 Moderate bearish | -1.0 Strong bearish
- **TEMA Confidence**: 1.0 Unanimous (3/3) | 0.67 Majority (2/3) | 0.33 Weak (1/3) | 0.0 No agreement
- **Volatility Scalar**: <0.8 Low vol (shorter periods) | 0.8-1.2 Normal | >1.2 High vol (longer periods)
- **Signals**: STRONG BUY | BUY | BUY THE DIP | WAIT | SELL THE TOP | SELL | STRONG SELL

## Technical Stack

- **yfinance** - Yahoo Finance market data API wrapper
- **pandas** - Time series data structures and analysis
- **numpy** - Vectorized numerical computation
- **ta** - Technical indicator library (ADX, moving averages)
- **requests** - HTTP client for FRED API integration
- **python-dotenv** - Environment configuration management
- **fear-and-greed** - CNN sentiment index data retrieval
- **openpyxl** - Excel file generation with conditional formatting and styling

## License

MIT License - Open source for research, personal, and commercial applications.
