# Weekly Market Analysis Tracker

A Python-based technical analysis tool that provides comprehensive weekly market reports combining macro indicators and technical analysis for multiple asset classes.

## Features

- **Macro Indicators**
  - Global Liquidity Index (GLI) - Fed Balance Sheet minus TGA and RRP
  - VIX volatility tracking with inverted VIX Z-Score (market regime detection)
  - Fear & Greed Index for stocks and crypto

- **Technical Analysis** (Daily & Weekly timeframes)
  - Trend detection using ADX and moving averages
  - Z-Score for overbought/oversold detection (20-day rolling)
  - Moving average distance analysis (20, 50, 200-day)

- **Default Asset Coverage**
  - ETFs: ISAC, SMH, URA, ROBO, ARKQ
  - Cryptocurrencies: BTC, ETH
  - Indices: S&P 500
  - Commodities: Gold, Silver

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

## Usage

Run the weekly market analysis:

```bash
python weekly_market_tracker.py
```

### Custom Tickers

You can track any ticker available on Yahoo Finance. Edit the `ASSETS` dictionary in `weekly_market_tracker.py`:

```python
ASSETS = {
    "ISAC": "ISAC.L",      # iShares MSCI ACWI (London)
    "SMH": "SMH",          # VanEck Semiconductor ETF
    "URA": "URA",          # Global X Uranium ETF
    "ROBO": "ROBO",        # ROBO Global Robotics ETF
    "ARKQ": "ARKQ",        # ARK Autonomous Tech ETF
    "BTCUSD": "BTC-USD",   # Bitcoin
    "ETHUSD": "ETH-USD",   # Ethereum
    "SPX": "^GSPC",        # S&P 500 Index
    "GOLD": "GC=F",        # Gold Futures
    "SILVER": "SI=F",      # Silver Futures
}
```

**Example custom portfolio (tech-focused):**

```python
ASSETS = {
    "AAPL": "AAPL",        # Apple
    "MSFT": "MSFT",        # Microsoft
    "NVDA": "NVDA",        # NVIDIA
    "GOOGL": "GOOGL",      # Alphabet
    "AMZN": "AMZN",        # Amazon
    "QQQ": "QQQ",          # Nasdaq 100 ETF
    "SPY": "SPY",          # S&P 500 ETF
    "TLT": "TLT",          # 20+ Year Treasury Bond ETF
    "BTCUSD": "BTC-USD",   # Bitcoin
}
```

**Finding Yahoo Finance tickers:**
- US Stocks: Use the stock symbol directly (e.g., `AAPL`, `TSLA`)
- International: Add exchange suffix (e.g., `ISAC.L` for London, `7203.T` for Tokyo)
- Crypto: Use format `SYMBOL-USD` (e.g., `BTC-USD`, `SOL-USD`)
- Indices: Use caret prefix (e.g., `^GSPC`, `^DJI`, `^IXIC`)
- Futures: Use format `SYMBOL=F` (e.g., `GC=F`, `CL=F`)

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
     VIX: 14.95 (Low) | 1/VIX: 0.0669
     1/VIX Z-Score: +0.31 -> Neutral

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
  TREND: Up | Down | Sideways | ADX: <20 Weak, 20-40 Mod, >40 Strong
  Z-SCORE: >+2 OB | <-2 OS | >+2.5 Extreme OB | <-2.5 Extreme OS
  1/VIX Z: >+1.5 Complacency | <-1.5 Fear | +/-0.5-1.5 Risk-On/Off
  F&G: 0-25 Ext Fear | 26-45 Fear | 46-55 Neutral | 56-75 Greed | 76-100 Ext Greed
  GLI: Expanding >1% | Contracting <-1% | Flat
==========================================================================================
```

## AI-Powered Analysis

For deeper portfolio rebalancing insights, feed the script output to an LLM using the provided `SYSPROMPT.MD`:

1. Run the script and copy the output
2. Use the system prompt from `SYSPROMPT.MD` with one of the recommended LLMs below
3. **Enable extended thinking/reasoning mode** for best analysis quality
4. Get actionable portfolio signals and rebalancing recommendations

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

### Example LLM Output

Given the script output above, an LLM with `SYSPROMPT.MD` produces:

**Table 1: Macro Summary**

| Indicator | Value | Signal | Implication |
| --------- | ----- | ------ | ----------- |
| GLI | $5744B (+1.68% 4wk) | Bullish | Expanding liquidity supports risk assets |
| VIX | 14.95 | Neutral | Low vol, cheap hedges available |
| 1/VIX Z | +0.31 | Neutral | Normal risk regime, no extremes |
| Stock F&G | 46 | Neutral | No contrarian signal |
| Crypto F&G | 21 | Bullish | Extreme Fear = contrarian buy zone |

**Table 2: Ticker Signals**

| Ticker | Price | Z-Score (D/W) | Signal | Key Drivers |
| ------ | ----- | ------------- | ------ | ----------- |
| ISAC | $109.28 | +1.40/+1.50 | HOLD | Uptrend aligned, upper zone both TFs |
| SMH | $360.13 | +0.01/+1.01 | HOLD | Daily sideways, weekly support intact |
| URA | $42.73 | -1.65/-0.84 | ACCUMULATE | Approaching OS, range-bound dip buy |
| BTCUSD | $87,649 | -0.15/-1.26 | ACCUMULATE | Weekly lower + Extreme Fear = contrarian |
| ETHUSD | $2,976 | +0.13/-1.13 | WAIT | ADX 26 downtrend, knife risk |
| GOLD | $4,332 | +0.11/+1.08 | HOLD | Strong weekly uptrend, not OB |
| SILVER | $70.98 | +0.95/+1.86 | HOLD | Strong trend, watch for +2 OB |

**Table 3: Rebalance Actions**

| Action | From | To | Rationale |
| ------ | ---- | -- | --------- |
| ACCUMULATE | Cash | URA | Z -1.65 lower zone, mean reversion play |
| ACCUMULATE | Cash | BTCUSD | Weekly Z -1.26 + Crypto F&G Extreme Fear |
| WATCH | - | SILVER | Weekly Z +1.86 nearing +2 OB threshold |
| HEDGE | - | Portfolio | VIX 14.95 = cheap puts available |

## Understanding GLI (Global Liquidity Index)

The GLI measures actual money available in the financial system using Fed data.

**Formula:** `GLI = Fed Balance Sheet - TGA - RRP`

### Components

| Term | FRED Code | Full Name | Description |
|------|-----------|-----------|-------------|
| **Fed BS** | `WALCL` | Fed Total Assets | Total assets held by the Federal Reserve |
| **TGA** | `WTREGEN` | Treasury General Account | US Treasury's checking account at the Fed |
| **RRP** | `RRPONTSYD` | Reverse Repo | Cash parked at the Fed by money market funds |

### Why Subtract TGA and RRP?

```
Fed Balance Sheet    = Money the Fed has "printed" (QE)
- TGA                = Money sitting idle at Treasury (not circulating)
- RRP                = Money parked at Fed overnight (not circulating)
────────────────────────────────────────────────────────────────────
= Net Liquidity      = Actual money available in financial system
```

### Market Effects

| Component | When It Rises | Market Effect |
|-----------|---------------|---------------|
| **Fed BS** | QE / asset purchases | Bullish (more liquidity) |
| **TGA** | Treasury accumulates cash | Bearish (drains liquidity) |
| **RRP** | Excess cash parked at Fed | Bearish (drains liquidity) |

### Interpreting GLI Trends

- **Expanding** (+1% over 4 weeks): More dollars chasing assets, bullish for risk assets
- **Contracting** (-1% over 4 weeks): Less liquidity, bearish, risk-off environment
- **Correlation**: GLI historically correlates with BTC, stocks, and risk assets

## Output Legend

- **Trend**: Uptrend | Downtrend | Sideways
- **ADX**: <20 Weak | 20-40 Moderate | >40 Strong
- **Z-Score**: >+2 Overbought | <-2 Oversold | >+2.5 Extreme OB | <-2.5 Extreme OS
- **1/VIX Z-Score**: >+1.5 Complacency | <-1.5 Fear | +/-0.5-1.5 Risk-On/Off
- **Fear & Greed**: 0-25 Extreme Fear | 26-45 Fear | 46-55 Neutral | 56-75 Greed | 76-100 Extreme Greed
- **GLI**: Expanding >1% | Contracting <-1% | Flat

## Dependencies

- yfinance - Market data retrieval
- pandas - Data manipulation
- numpy - Numerical operations
- ta - Technical analysis indicators (ADX)
- requests - API calls
- python-dotenv - Environment variable management
- fear-and-greed - CNN Fear & Greed Index

## License

MIT License - feel free to use and modify for personal or commercial use.
