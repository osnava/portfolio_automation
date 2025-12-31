# Weekly Market Analysis Tracker

A Python-based technical analysis tool that provides comprehensive weekly market reports combining macro indicators and technical analysis for multiple asset classes.

## Features

- **Macro Indicators**

  - Global Liquidity Index (GLI) - Fed Balance Sheet minus TGA and RRP
  - VIX volatility tracking
  - Fear & Greed Index for stocks and crypto
- **Technical Analysis** (Daily & Weekly timeframes)

  - Trend detection using ADX and moving averages
  - Stochastic RSI with overbought/oversold zones
  - MACD with momentum analysis
  - Moving average distance analysis (20, 50, 200-day)
- **Asset Coverage**

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

The script will output a formatted report with:

- Current macro market conditions
- Technical analysis for each tracked asset
- Trend direction and strength
- Key indicator signals

## AI-Powered Analysis

For deeper portfolio rebalancing insights, you can feed the script output to an LLM using the provided `SYSPROMPT.MD`:

1. Run the script and copy the output
2. Use the system prompt from `SYSPROMPT.MD` with one of the recommended LLMs below
3. **Enable extended thinking/reasoning mode** for best analysis quality
4. Get actionable portfolio signals and rebalancing recommendations

### Recommended Models (as of Dec 2025)

**Proprietary Models (API-based):**

- **Claude Opus 4.5** (`claude-opus-4-5-20251124`) - Most intelligent, best reasoning (Nov 2025)
- **Claude Sonnet 4.5** (`claude-sonnet-4-5-20250929`) - Best for complex agents and coding (Sep 2025)
- **GPT-5** (`gpt-5`) - OpenAI's latest with unified reasoning (Aug 2025)
- **Gemini 2.0** (`gemini-2.0-flash-thinking-exp`) - Google's latest with thinking mode

**Open-Source Models (Self-hosted):**

- **DeepSeek R1** - 236B params, top open-source for logic & reasoning
- **Qwen 2.5 72B** - Excellent for research tasks, multilingual, strong reasoning
- **Llama 3.3 70B** - Meta's latest, clean controllable output
- **Mistral Large 2** - 123B params, near-GPT-4 performance, efficient

## Output Legend

- **Trend**: 📈 Uptrend | 📉 Downtrend | ↔️ Sideways
- **ADX**: <20 Weak | 20-40 Moderate | >40 Strong
- **Stoch RSI**: >80 Overbought | <20 Oversold | ^ Bull cross | v Bear cross
- **MACD**: Bullish/Bearish with Strengthening/Weakening momentum
- **Fear & Greed**: 0-25 Extreme Fear | 26-45 Fear | 46-55 Neutral | 56-75 Greed | 76-100 Extreme Greed
- **GLI**: 📈 Expanding >1% | 📉 Contracting <-1% | ➡️ Flat

## Dependencies

- yfinance - Market data retrieval
- pandas - Data manipulation
- numpy - Numerical operations
- ta - Technical analysis indicators
- requests - API calls
- python-dotenv - Environment variable management
- fear-and-greed - CNN Fear & Greed Index

## License

MIT License - feel free to use and modify for personal or commercial use.
