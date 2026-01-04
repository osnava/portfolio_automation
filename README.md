# Quantitative Market Analysis Framework

A systematic approach to multi-asset analysis combining macro liquidity metrics, volatility regime detection, and statistical technical indicators across equities, cryptocurrencies, and commodities.

## Methodology

- **Macro Liquidity Metrics**

  - Global Liquidity Index (GLI) - Net Fed liquidity after TGA and RRP adjustments
  - VIX volatility regime classification via normalized Z-Score transformation
  - Sentiment indicators (Fear & Greed indices) for mean reversion signals
- **Statistical Technical Analysis** (Dual-timeframe: Daily & Weekly)

  - Directional Movement Index (ADX) for trend strength quantification
  - Rolling Z-Score (20-period) for statistical overbought/oversold levels
  - Moving average distance metrics (20/50/200-period) for trend confirmation
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

Execute systematic analysis routine:

```bash
python weekly_market_tracker.py
```

### Portfolio Customization

Configure universe constituents via the `ASSETS` dictionary in `weekly_market_tracker.py` (supports all Yahoo Finance tickers):

```python
ASSETS = {
    "iShares MSCI ACWI ETF": "ISAC.L",
    "VanEck Semiconductor ETF": "SMH",
    "Global X Uranium ETF": "URA",
    "ROBO Global Robotics and Automation ETF": "ROBO",
    "ARK Autonomous Technology & Robotics ETF": "ARKQ",
    "Bitcoin USD": "BTC-USD",
    "Ethereum USD": "ETH-USD",
    "S&P 500": "^GSPC",
    "Gold Futures": "GC=F",
    "Silver Futures": "SI=F",
}
```

**Alternative universe specification (technology sector concentration):**

```python
ASSETS = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Alphabet": "GOOGL",
    "Amazon": "AMZN",
    "Nasdaq 100 ETF": "QQQ",
    "S&P 500 ETF": "SPY",
    "20+ Year Treasury Bond ETF": "TLT",
    "Bitcoin USD": "BTC-USD",
}
```

**Ticker convention reference:**

- US Equities: Direct symbol notation (`AAPL`, `TSLA`)
- International Equities: Exchange-suffixed format (`ISAC.L` for LSE, `7203.T` for TSE)
- Digital Assets: USD pair notation (`BTC-USD`, `SOL-USD`)
- Benchmark Indices: Caret prefix (`^GSPC`, `^DJI`, `^IXIC`)
- Futures Contracts: Continuous contract notation (`GC=F`, `CL=F`)

## Example Output

```
==========================================================================================
  WEEKLY MARKET ANALYSIS - Wednesday, 2025-12-31 16:42
==========================================================================================

  MACRO INDICATORS
  --------------------------------------------------

  Global Liquidity Index:
     Net Liquidity:  $5744.11B  Expanding
     Fed: $6581.23B | TGA: $837.12B | RRP: $0.11B | Date: 2025-12-24
     WoW: +$20.35B (+0.36%)
     4-Week: +$95.08B (+1.68%)
     12-Week: $-37.86B (-0.65%)

  Volatility & Regime:
     VIX: 14.95 (Low)
     -Z(VIX): +0.31 -> Neutral

  Sentiment:
     Fear & Greed (Stocks): 46 - Neutral
     Fear & Greed (Crypto): 21 - Extreme Fear

==========================================================================================
  ASSET ANALYSIS
==========================================================================================

------------------------------------------------------------------------------------------
  BTCUSD (BTC-USD)
------------------------------------------------------------------------------------------

  $87,649.23

  DAILY: Sideways/Choppy (Weak, ADX: 18.0)
     Z-Score: -0.15 (Neutral)
     MAs: MA20: 0.2% down | MA50: 2.4% down | MA200: 18.1% down

  WEEKLY: Sideways/Choppy (Moderate, ADX: 23.4)
     Z-Score: -1.26 (Lower)
     MAs: MA20: 15.2% down | MA50: 13.7% down

------------------------------------------------------------------------------------------
  GOLD (GC=F)
------------------------------------------------------------------------------------------

  $4,332.10

  DAILY: Uptrend (Moderate, ADX: 30.0)
     Z-Score: +0.11 (Neutral)
     MAs: MA20: 0.3% up | MA50: 3.8% up | MA200: 20.1% up

  WEEKLY: Uptrend (Strong, ADX: 67.1)
     Z-Score: +1.08 (Upper)
     MAs: MA20: 8.5% up | MA50: 23.7% up

==========================================================================================
  QUICK REFERENCE
==========================================================================================
  TREND: Up | Down | Sideways | ADX: <20 Weak, 20-25 Mod, >25 Strong
  Z-SCORE: >+2 OB | <-2 OS | >+2.5 Extreme OB | <-2.5 Extreme OS
  -Z(VIX): >+1.5 Complacency | <-1.5 Fear | +/-0.5-1.5 Risk-On/Off
  F&G: 0-25 Ext Fear | 26-45 Fear | 46-55 Neutral | 56-75 Greed | 76-100 Ext Greed
  GLI: Expanding >1% | Contracting <-1% | Flat
==========================================================================================
```

## LLM-Enhanced Signal Generation

Augment quantitative signals with qualitative factor analysis by integrating output with large language models configured via `SYSPROMPT.MD`:

1. Execute analysis routine and capture output
2. Configure LLM with system prompt from `SYSPROMPT.MD`
3. **Enable extended reasoning mode** for optimal inference quality
4. Extract actionable alpha signals and portfolio rebalancing recommendations

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

Representative LLM-generated analysis using `SYSPROMPT.MD` configuration:

**Table 1: Macro Regime Assessment**

| Indicator  | Value               | Signal  | Directional Bias                               |
| ---------- | ------------------- | ------- | ---------------------------------------------- |
| GLI        | $5744B (+1.68% 4wk) | Long    | Expanding liquidity favors risk-on positioning |
| VIX        | 14.95               | Neutral | Low implied vol, favorable hedge cost          |
| -Z(VIX)    | +0.31               | Neutral | No regime extreme detected                     |
| Stock F&G  | 46                  | Neutral | No contrarian conviction signal                |
| Crypto F&G | 21                  | Long    | Extreme fear zone, contrarian entry            |

**Table 2: Security-Level Signals**

| Ticker | Price   | Z-Score (D/W) | Position   | Technical Thesis                          |
| ------ | ------- | ------------- | ---------- | ----------------------------------------- |
| ISAC   | $109.28 | +1.40/+1.50   | Hold       | Dual-TF uptrend, elevated but not extreme |
| SMH    | $360.13 | +0.01/+1.01   | Hold       | Daily consolidation, weekly structure intact |
| URA    | $42.73  | -1.65/-0.84   | Accumulate | Statistical oversold, mean reversion setup |
| BTCUSD | $87,649 | -0.15/-1.26   | Accumulate | Weekly Z-score + sentiment divergence     |
| ETHUSD | $2,976  | +0.13/-1.13   | Avoid      | ADX 26 downtrend, momentum unfavorable    |
| GOLD   | $4,332  | +0.11/+1.08   | Hold       | Strong weekly trend, not extended         |
| SILVER | $70.98  | +0.95/+1.86   | Hold       | Monitor for +2σ threshold breach          |

**Table 3: Portfolio Action Items**

| Action     | From | To        | Quantitative Rationale                         |
| ---------- | ---- | --------- | ---------------------------------------------- |
| Accumulate | Cash | URA       | Z-score -1.65, mean reversion probability high |
| Accumulate | Cash | BTCUSD    | Weekly Z -1.26 + sentiment extreme divergence  |
| Monitor    | -    | SILVER    | Weekly Z +1.86 approaching +2σ overextension   |
| Hedge      | -    | Portfolio | VIX 14.95 implies attractive put premium       |

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

- **Trend Classification**: Uptrend | Downtrend | Consolidation
- **ADX (Directional Strength)**: <20 Weak trend | 20-25 Moderate | >25 Strong
- **Z-Score (Price Deviation)**: >+2 Statistical OB | <-2 Statistical OS | >+2.5 Extreme | <-2.5 Extreme
- **-Z(VIX) Regime**: >+1.5 Complacency | <-1.5 Elevated fear | +/-0.5-1.5 Transitional
- **Sentiment Index**: 0-25 Extreme Fear | 26-45 Fear | 46-55 Neutral | 56-75 Greed | 76-100 Extreme Greed
- **GLI Trend**: Expanding >1% | Contracting <-1% | Neutral

## Technical Stack

- **yfinance** - Yahoo Finance market data API wrapper
- **pandas** - Time series data structures and analysis
- **numpy** - Vectorized numerical computation
- **ta** - Technical indicator library (ADX, moving averages)
- **requests** - HTTP client for FRED API integration
- **python-dotenv** - Environment configuration management
- **fear-and-greed** - CNN sentiment index data retrieval

## License

MIT License - Open source for research, personal, and commercial applications.
