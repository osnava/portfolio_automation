# Quantitative Market Analysis Framework

A systematic approach to multi-asset analysis combining macro liquidity metrics, volatility regime detection, and statistical technical indicators across equities, cryptocurrencies, and commodities.

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
  - Daily Z-Score (20-period) for near-term entry/exit timing
  - TEMA cross detection (20/50, 50/200) for trend change signals
  - Daily ADX for intraday trend strength
  - TEMA alignment scoring (3-point: price, TEMA20, TEMA50, TEMA200)

  **Multi-Timeframe Decision Logic:**
  - Weekly determines **direction** (trend/regime identification)
  - Daily determines **timing** (entry/exit precision)
  - Example: Weekly BUY + Daily Bullish TEMA Cross = STRONG BUY (highest conviction)

- **Universe Coverage**

  - Equity ETFs: ISAC, SMH, URA, ROBO, ARKQ
  - Digital Assets: BTC, ETH
  - Benchmark Indices: S&P 500
  - Precious Metals: Gold, Silver futures

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
- **Macro**: GLI, VIX, -Z(VIX), Fear & Greed indices
- **Weekly**: Asset signals with TSMOM, Z-Score, MA Score, ADX, Regime
- **Momentum**: Detailed 4w/12w/26w percentage returns
- **Daily**: TEMA analysis with cross detection and daily Z-scores

**File format:** `output/YYYYMMDD_HHMM_ANALYSIS.xlsx` (e.g., `20260110_1617_ANALYSIS.xlsx`)

**Features:**
- ✅ Conditional formatting (color-coded cells: green=positive, red=negative)
- ✅ Auto-optimized column widths
- ✅ Numeric data types for Excel formulas
- ✅ Professional color scheme for quick visual analysis
- ✅ Adaptive formatting (automatically adjusts to any number of assets)

## Project Structure

```
trading/
├── weekly_market_tracker.py    # Main analysis script
├── sysprompt.md                 # LLM analysis instructions
├── QF_TERMINOLOGY.md            # Complete terminology reference
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .env                         # API keys (create this)
├── .gitignore                   # Git exclusions
├── tickers/                     # Portfolio definitions
│   ├── assets.json              # Default portfolio (11 assets)
│   ├── assets_jorge.json        # Extended portfolio (73 assets)
│   └── assets_mag7.json         # Magnificent 7 tech stocks
└── output/                      # Generated analysis files (gitignored)
    └── YYYYMMDD_HHMM_ANALYSIS.xlsx
```

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
  "S&P 500": "^GSPC",
  "Gold Futures": "GC=F",
  "Silver Futures": "SI=F"
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
| Indicator | Value | Signal | Detail |
|-----------|-------|--------|--------|
| GLI | 5777.45 | Expanding | 4w: +1.73% \| 12w: +0.52% |
| VIX | 17.23 | Normal | - |
| -Z(VIX) | +0.45 | Neutral | - |
| F&G Stocks | 48 | Neutral | - |
| F&G Crypto | 52 | Neutral | - |

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
| Asset | Price | Z-Score_Daily | TEMA20 | TEMA50 | TEMA200 | Cross_20_50 | Cross_50_200 | TEMA_Alignment | ADX_Daily |
|-------|-------|---------------|--------|--------|---------|-------------|--------------|----------------|-----------|
| SMH | 389.22 | +1.45 | 385.67 | 372.34 | 298.12 | None | None | 3/3 | 28.5 |
| URA | 50.31 | +0.89 | 49.87 | 47.23 | 41.56 | Bullish Cross | None | 3/3 | 31.2 |

**Color coding:**
- 🟢 Green: Positive values (TSMOM >0%, returns >0%, above MAs)
- 🔴 Red: Negative values (TSMOM <0%, returns <0%, below MAs)
- 🟡 Yellow: Overbought Z-scores (+2.0 and above)
- ⚪ White: Neutral values

## LLM-Enhanced Signal Generation

Augment quantitative signals with qualitative factor analysis by integrating XLSX output with large language models configured via `sysprompt.md`:

1. Execute analysis routine to generate XLSX file
2. Upload XLSX file to LLM (Claude, ChatGPT, Gemini)
3. Configure LLM with system prompt from `sysprompt.md`
4. Select risk profile: 🥛 Conservative, 📊 Moderate, or 🌶️ Aggressive
5. **Enable extended reasoning mode** for optimal inference quality (Claude "thinking", ChatGPT "o1", Gemini "thinking")
6. LLM analyzes all 4 sheets and generates actionable signals (STRONG BUY, BUY, WAIT, SELL, STRONG SELL) with portfolio rebalancing recommendations

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

### Sample Signal Output

Representative LLM-generated analysis using `sysprompt.md` configuration (Moderate profile):

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
- **Signals**: STRONG BUY | BUY | WAIT | SELL | STRONG SELL

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
