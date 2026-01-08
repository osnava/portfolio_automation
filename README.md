# Quantitative Market Analysis Framework

A systematic approach to multi-asset analysis combining macro liquidity metrics, volatility regime detection, and statistical technical indicators across equities, cryptocurrencies, and commodities.

## Methodology

- **Macro Liquidity Metrics**

  - Global Liquidity Index (GLI) - Net Fed liquidity after TGA and RRP adjustments
  - VIX volatility regime classification via normalized Z-Score transformation
  - Sentiment indicators (Fear & Greed indices) for mean reversion signals
- **Statistical Technical Analysis** (Weekly timeframe)

  - Time-Series Momentum (TSMOM) - Multi-period momentum score (4w/12w/26w lookbacks)
  - MA Score - 7-point moving average alignment indicator (20/50/100/200-period)
  - Regime Classification - TRENDING_UP, TRENDING_DOWN, MEAN_REVERT, CHOPPY, NEUTRAL
  - Directional Movement Index (ADX) for trend strength quantification
  - Rolling Z-Score (20-period) for statistical overbought/oversold levels
  - Moving average distance metrics (20/50/100/200-period) for trend confirmation
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
python weekly_market_tracker.py assets_mag7.json
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

```
┌─────────────────────────────┐
│ WEEKLY MARKET ANALYSIS      │
│ Tuesday, 2026-01-07 10:15   │
│ Portfolio: assets           │
└─────────────────────────────┘

                               MACRO INDICATORS
┌─────────────────┬────────────┬─────────────┬────────────────────────────────┐
│ Indicator       │      Value │   Signal    │ Detail                         │
├─────────────────┼────────────┼─────────────┼────────────────────────────────┤
│ Global          │    $5,803B │     📈      │ 4w: +3.65% | 12w: +0.34%       │
│ Liquidity       │            │  Expanding  │                                │
│ VIX             │      15.27 │   Normal    │                                │
│ -Z(VIX)         │      +0.90 │   Risk-On   │                                │
│ F&G Stocks      │         51 │   Neutral   │                                │
│ F&G Crypto      │         42 │    Fear     │                                │
└─────────────────┴────────────┴─────────────┴────────────────────────────────┘

                                ASSET ANALYSIS
┌─────────────┬────────────┬────────┬───────┬──────┬──────┬───────────────────┐
│ Asset       │      Price │   Z    │ TSMOM │  MA  │ ADX  │ Regime            │
├─────────────┼────────────┼────────┼───────┼──────┼──────┼───────────────────┤
│ ISAC.L      │    £102.45 │ +1.23  │ 1.00  │ 7/7  │  31  │ TRENDING_UP       │
│ SMH         │    $245.78 │ -0.85  │ 0.67  │ 6/7  │  28  │ TRENDING_UP       │
│ PLTR        │     $85.20 │ +2.15  │ 1.00  │ 7/7  │  45  │ MEAN_REVERT_SELL  │
│ BTC-USD     │ $92,340.00 │ -1.42  │ 0.33  │ 4/7  │  19  │ CHOPPY            │
│ ^GSPC       │  $5,918.00 │ +0.55  │ 1.00  │ 7/7  │  26  │ TRENDING_UP       │
└─────────────┴────────────┴────────┴───────┴──────┴──────┴───────────────────┘

                               MOMENTUM DETAILS

  Asset         4w   12w   26w   MA Distance
 ─────────────────────────────────────────────────────────────────────────────
  ISAC.L       +2…   +3…   +5…   MA20: 1.8%↑ | MA50: 5.2%↑ | MA100: 12.1%↑ |
                                 MA200: 18.5%↑
  SMH          -1…   +2…   +3…   MA20: 0.9%↓ | MA50: 3.1%↑ | MA100: 8.7%↑ |
                                 MA200: 15.2%↑
  PLTR         +8…   +12…  +15…  MA20: 8.5%↑ | MA50: 18.2%↑ | MA100: 35.6%↑
                                 | MA200: 68.9%↑


┌─────────────────────────────────────────────────────────────────────────────┐
│ MACRO REGIME                                                                │
│ GLI 📈 Expanding (+3.6% 4w) | -Z(VIX) = +0.90 → Risk-On                     │
│ ✓ GLI EXPANDING: Risk-on favored                                            │
│                                                                             │
│ REFERENCE                                                                   │
│ Z-Score: >+2 OB | <-2 OS | >+2.5 Extreme OB | <-2.5 Extreme OS              │
│ TSMOM: 1.0=All↑ | 0.67=Mostly↑ | 0.33=Mostly↓ | 0.0=All↓                    │
│ MA Score: 7/7=Strong↑ | 5-6=↑ | 3-4=Mixed | 0-2=↓                           │
│ ADX: <20=Weak | 20-25=Mod | >25=Strong                                      │
│ Regime: TRENDING_UP | TRENDING_DOWN | MEAN_REVERT | CHOPPY                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## LLM-Enhanced Signal Generation

Augment quantitative signals with qualitative factor analysis by integrating output with large language models configured via `sysprompt.md`:

1. Execute analysis routine and capture output
2. Configure LLM with system prompt from `sysprompt.md`
3. Select risk profile: 🥛 Conservative, 📊 Moderate, or 🌶️ Aggressive
4. **Enable extended reasoning mode** for optimal inference quality
5. Extract actionable alpha signals (STRONG BUY, BUY, WAIT, SELL, STRONG SELL) and portfolio rebalancing recommendations

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

| Ticker | Price   | Z-Score | TSMOM | Regime           | Signal      | Key Drivers                                    |
| ------ | ------- | ------- | ----- | ---------------- | ----------- | ---------------------------------------------- |
| ISAC.L | £102.45 | +1.23   | 1.00  | TRENDING_UP      | BUY         | Strong trend + TSMOM 1.0 + MA 7/7 + ADX 31    |
| SMH    | $245.78 | -0.85   | 0.67  | TRENDING_UP      | STRONG BUY  | Oversold + uptrend + TSMOM ≥0.67               |
| PLTR   | $85.20  | +2.15   | 1.00  | MEAN_REVERT_SELL | SELL        | Extreme overbought Z +2.15, mean reversion due |
| BTC    | $92,340 | -1.42   | 0.33  | CHOPPY           | WAIT        | TSMOM 0.33 below threshold (0.67), ADX weak    |
| ^GSPC  | $5,918  | +0.55   | 1.00  | TRENDING_UP      | BUY         | Trend intact, not overbought, TSMOM 1.0        |

**Table 3: Rebalance Actions**

| Action | From | To     | Rationale                                                |
| ------ | ---- | ------ | -------------------------------------------------------- |
| BUY    | Cash | SMH    | STRONG BUY: Oversold + TRENDING_UP + all thresholds met |
| BUY    | Cash | ^GSPC  | BUY: Clean trend signal, broad market exposure           |
| SELL   | PLTR | Cash   | Z +2.15 extreme OB, take profits on parabolic move       |
| WAIT   | -    | BTC    | Momentum conflict, await TSMOM ≥0.67 for entry           |

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
- **TSMOM (Momentum)**: 1.0 All positive | 0.67 Mostly positive | 0.33 Mostly negative | 0.0 All negative
- **MA Score (Alignment)**: 7/7 Strong uptrend | 5-6/7 Uptrend | 3-4/7 Mixed | 0-2/7 Downtrend
- **ADX (Trend Strength)**: <20 Weak | 20-25 Moderate | >25 Strong | >40 Very strong
- **Z-Score (Price Deviation)**: >+2 Statistical OB | <-2 Statistical OS | >+2.5 Extreme | <-2.5 Extreme
- **-Z(VIX) Regime**: >+1.5 Complacency | <-1.5 Elevated fear | +/-0.5-1.5 Transitional
- **Sentiment Index**: 0-25 Extreme Fear | 26-45 Fear | 46-55 Neutral | 56-75 Greed | 76-100 Extreme Greed
- **GLI Trend**: Expanding >1% | Contracting <-1% | Neutral
- **Signals**: STRONG BUY | BUY | WAIT | SELL | STRONG SELL

## Technical Stack

- **yfinance** - Yahoo Finance market data API wrapper
- **pandas** - Time series data structures and analysis
- **numpy** - Vectorized numerical computation
- **ta** - Technical indicator library (ADX, moving averages)
- **requests** - HTTP client for FRED API integration
- **python-dotenv** - Environment configuration management
- **fear-and-greed** - CNN sentiment index data retrieval
- **rich** - Terminal styling and formatted output (tables, colors, panels)

## License

MIT License - Open source for research, personal, and commercial applications.
