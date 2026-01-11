# Quantitative Finance Terminology Reference

Comprehensive glossary of quantitative finance terms used in this trading framework, organized by domain.

---

## 1. Macro Liquidity Metrics

### Global Liquidity Index (GLI)
**Definition:** Net dollar liquidity available in the financial system after accounting for sterilization mechanisms.

**Formula:**
```
GLI = Fed Balance Sheet - TGA - RRP
```

**Components:**
- **Fed Balance Sheet (WALCL):** Total assets held by the Federal Reserve, primarily acquired through quantitative easing (QE) programs
- **TGA (Treasury General Account - WTREGEN):** US Treasury's operating cash account at the Fed; funds sequestered here are not circulating in markets
- **RRP (Reverse Repo - RRPONTSYD):** Overnight facility where money market funds park excess cash, effectively sterilizing liquidity

**Interpretation:**
- **Expanding (>+1% 4-week):** Net liquidity injection favors risk-on positioning
- **Contracting (<-1% 4-week):** Liquidity withdrawal creates risk-off environment
- **Correlation:** Historically positive correlation with BTC, equities, and high-beta assets

**Usage in framework:** Primary macro regime filter for portfolio risk bias

---

## 2. Volatility & Regime Indicators

### VIX (CBOE Volatility Index)
**Definition:** Implied volatility index derived from S&P 500 option prices, measuring 30-day forward expected volatility.

**Interpretation:**
- **<15:** Low volatility regime, cheap hedges available
- **15-20:** Normal volatility
- **20-30:** Elevated volatility
- **>30:** High volatility, fear regime

**Common names:** "Fear gauge", "fear index"

---

### -Z(VIX) | Inverted VIX Z-Score
**Definition:** Normalized, inverted, and smoothed VIX deviation used for market regime classification.

**Calculation:**
1. Calculate 52-week rolling Z-score of VIX
2. Invert the sign (multiply by -1)
3. Apply 5-period EMA smoothing

**Formula:**
```
Raw Z-Score = (VIX - μ₅₂) / σ₅₂
-Z(VIX) = EMA₅(-1 × Z-Score)
```

**Regime classification:**
| -Z(VIX) Range | Regime | Market State |
|---------------|---------|--------------|
| >+1.5 | Complacency | Overbought, trim winners, add hedges |
| +0.5 to +1.5 | Risk-On | Bullish but cautious |
| -0.5 to +0.5 | Neutral | No regime extreme |
| -1.5 to -0.5 | Risk-Off | Defensive positioning |
| <-1.5 | Fear | Contrarian buy opportunity |

**Why invert?** Raw VIX spikes during fear (positive Z), but we want positive values to represent "low fear" for intuitive interpretation.

---

## 3. Technical Analysis Indicators

### ADX (Average Directional Index)
**Definition:** Trend strength indicator measuring the degree of directional movement, regardless of direction.

**Range:** 0-100 (typically 0-60 in practice)

**Interpretation:**
- **<20:** Weak trend, choppy/sideways market
- **20-25:** Moderate trend
- **>25:** Strong trend
- **>40:** Very strong trend

**Related indicators:**
- **+DI (Plus Directional Indicator):** Upward price movement strength
- **-DI (Minus Directional Indicator):** Downward price movement strength

**Signal logic:** ADX >25 + (+DI > -DI) = strong uptrend

**Usage in framework:** Validates trend quality before taking directional positions

---

### Moving Average (MA)
**Definition:** Rolling arithmetic mean of price over N periods, used for trend identification and support/resistance.

**Common periods:**
- **MA20:** Short-term trend (approximately 1 month of trading days)
- **MA50:** Medium-term trend (approximately 2.5 months)
- **MA100:** Intermediate trend (approximately 5 months)
- **MA200:** Long-term trend (approximately 10 months), major S/R level

**MA Distance Metric:**
```
Distance% = ((Price - MA) / MA) × 100
```

**Interpretation:**
- **Positive distance:** Price above MA (bullish)
- **Negative distance:** Price below MA (bearish)
- **Large magnitude:** Potential mean reversion opportunity

---

### MA Score (7-Point Alignment)
**Definition:** Composite trend strength metric based on moving average alignment.

**Calculation:** Score 0-7 based on:
1. Price > MA20
2. Price > MA50
3. Price > MA100
4. Price > MA200
5. MA20 > MA50
6. MA50 > MA100
7. MA100 > MA200

**Interpretation:**
- **7/7:** Perfect bullish alignment, strong uptrend
- **5-6/7:** Bullish structure, uptrend
- **3-4/7:** Mixed signals, choppy/transitional
- **0-2/7:** Bearish structure, downtrend

**Usage in framework:** Confirms trend strength for signal generation

---

### EMA (Exponential Moving Average)
**Definition:** Weighted moving average giving more importance to recent prices, responds faster to price changes than simple MA.

**Formula:**
```
EMA_t = (Price_t × α) + (EMA_{t-1} × (1 - α))
where α = 2 / (N + 1)
```

**Usage in framework:** Applied to smooth the -Z(VIX) signal (5-period EMA)

---

### TEMA (Triple Exponential Moving Average)
**Definition:** Triple-smoothed moving average that reduces lag while maintaining smoothness, used for faster trend detection and cross signals.

**Formula:**
```
EMA1 = EMA(Price, N)
EMA2 = EMA(EMA1, N)
EMA3 = EMA(EMA2, N)

TEMA = 3 × EMA1 - 3 × EMA2 + EMA3
```

**Common periods:**
- **TEMA20:** Short-term trend (daily timeframe)
- **TEMA50:** Medium-term trend
- **TEMA200:** Long-term trend

**TEMA Distance Metric:**
```
TEMA_Dist_% = ((Price - TEMA) / TEMA) × 100
```

**Cross Detection:**
- **Bullish Cross:** TEMA_fast crosses above TEMA_slow (e.g., TEMA20 > TEMA50 when previously TEMA20 ≤ TEMA50)
- **Bearish Cross:** TEMA_fast crosses below TEMA_slow

**TEMA Alignment:** Score 0-3 based on:
1. Price > TEMA20
2. TEMA20 > TEMA50
3. TEMA50 > TEMA200

**Interpretation:**
- **3/3:** Perfect bullish alignment, strong uptrend
- **2/3:** Moderate bullish structure
- **1/3:** Mixed signals
- **0/3:** Bearish structure

**Usage in framework:** Daily timeframe cross detection for entry/exit timing confirmation

---

## 4. Statistical Measures

### Z-Score (Standard Score)
**Definition:** Number of standard deviations a data point is from the mean, used to identify statistical extremes.

**Formula:**
```
Z = (X - μ) / σ

Where:
X = Current value
μ = Mean (rolling N-period)
σ = Standard deviation (rolling N-period)
```

**Interpretation zones:**
| Z-Score Range | Classification | Trading Implication |
|---------------|----------------|---------------------|
| >+2.5 | Extreme Overbought | High probability mean reversion setup |
| +2.0 to +2.5 | Overbought | Reduce/exit longs |
| +1.0 to +2.0 | Upper zone | Caution on new longs |
| -1.0 to +1.0 | Neutral zone | Normal distribution range |
| -2.0 to -1.0 | Lower zone | Accumulation opportunity |
| -2.5 to -2.0 | Oversold | Strong buy signal |
| <-2.5 | Extreme Oversold | Very high probability reversal |

**Window used:** 20 periods (weekly timeframe in this framework)

**Properties:**
- Assumes normal distribution
- Stationary in mean-reverting markets
- ~68% of data falls within ±1σ, ~95% within ±2σ

---

### Standard Deviation (σ)
**Definition:** Measure of dispersion/volatility around the mean.

**Formula:**
```
σ = √(Σ(X_i - μ)² / N)
```

**Usage:** Denominator in Z-score calculation; larger σ = higher volatility

---

### Mean (μ)
**Definition:** Arithmetic average of N observations.

**Formula:**
```
μ = Σ(X_i) / N
```

---

### Rolling Window
**Definition:** Moving subset of data used for calculating statistics, slides forward one period at a time.

**Example:** 20-period rolling window for Z-score means:
- At time t: use data from t-19 to t
- At time t+1: use data from t-18 to t+1

---

## 5. Market Sentiment Indicators

### Fear & Greed Index (Stocks)
**Source:** CNN Business

**Range:** 0-100

**Methodology:** Composite of 7 indicators:
1. Stock price momentum (S&P 500 vs 125-day MA)
2. Stock price strength (NYSE highs vs lows)
3. Stock price breadth (advancing vs declining volume)
4. Put/call options ratio
5. Junk bond demand (spread vs investment grade)
6. Market volatility (VIX)
7. Safe haven demand (stocks vs treasuries)

**Classification:**
- **0-25:** Extreme Fear (contrarian buy opportunity)
- **26-45:** Fear (cautious)
- **46-55:** Neutral
- **56-75:** Greed (trim positions)
- **76-100:** Extreme Greed (contrarian sell signal)

---

### Fear & Greed Index (Crypto)
**Source:** Alternative.me

**Range:** 0-100

**Methodology:** Composite of:
1. Volatility (25%)
2. Market momentum/volume (25%)
3. Social media sentiment (15%)
4. Dominance (10%)
5. Trends (Google searches) (10%)
6. Surveys (15%)

**Classification:** Same as stocks (0-25 Extreme Fear through 76-100 Extreme Greed)

**Strategy:** Used as contrarian indicator (buy fear, sell greed)

---

## 6. Price Action & Trend Analysis

### Trend Classification
**Definitions:**
- **Uptrend:** Higher highs and higher lows, price above key MAs, +DI > -DI
- **Downtrend:** Lower highs and lower lows, price below key MAs, -DI > +DI
- **Consolidation/Sideways:** Price oscillating in range, ADX <20, choppy directional indicators

**Trend Strength:**
- **Weak:** ADX <20
- **Moderate:** ADX 20-25
- **Strong:** ADX >25

---

### Overbought (OB)
**Definition:** Price has risen too far too fast relative to historical norms, statistically likely to revert.

**Identification:** Z-score >+2.0 (statistical OB) or >+2.5 (extreme OB)

---

### Oversold (OS)
**Definition:** Price has fallen too far too fast, statistically likely to bounce.

**Identification:** Z-score <-2.0 (statistical OS) or <-2.5 (extreme OS)

---

### Mean Reversion
**Definition:** Statistical tendency for prices to revert toward the historical mean after extreme deviations.

**Application:** Buy oversold (Z <-2), sell overbought (Z >+2)

**Failure modes:** Strong trends can remain "overbought" for extended periods (requires ADX confirmation)

---

### Momentum
**Definition:** Rate of price acceleration; persistent directional movement.

**Indicators:** ADX strength, MA slope, sequential higher highs (uptrend) or lower lows (downtrend)

---

### TSMOM (Time-Series Momentum)
**Definition:** Composite momentum metric measuring average percentage return across multiple lookback periods.

**Calculation:**
1. Calculate percentage returns for 4-week, 12-week, and 26-week lookbacks
2. Average the three percentage returns
3. Express as percentage (e.g., +15.3%, -5.2%)

**Formula:**
```
R_4w = ((Price_current / Price_4w_ago) - 1) × 100
R_12w = ((Price_current / Price_12w_ago) - 1) × 100
R_26w = ((Price_current / Price_26w_ago) - 1) × 100

TSMOM_% = (R_4w + R_12w + R_26w) / 3
```

**Interpretation:**
| TSMOM_% Range | Meaning | Trading Bias |
|---------------|---------|--------------|
| >+15% | Strong positive momentum across all timeframes | Strong hold/buy |
| +5% to +15% | Moderate positive momentum | Lean bullish |
| +2% to +5% | Weak positive momentum | Cautiously bullish |
| -2% to +2% | Neutral/choppy momentum | Wait/hold |
| -5% to -2% | Weak negative momentum | Cautiously bearish |
| <-5% | Strong negative momentum | Exit/avoid |

**Example:** If 4w return = +8%, 12w return = +12%, 26w return = +10%, then TSMOM = +10%

**Usage in framework:** Primary momentum filter; must agree with Z-score for action signals

---

## 7. Trading Signals & Actions

### Signal Taxonomy (by conviction level)

**Note:** Tm = TSMOM_% threshold (Conservative: +10%, Moderate: +5%, Aggressive: +2%)

**STRONG BUY**
- TRENDING_UP regime + TSMOM_% ≥Tm + MA Score ≥MAm + Z <-Zt
- Highest conviction long entry
- Oversold asset in confirmed uptrend with multi-factor alignment

**BUY**
- TRENDING_UP regime + TSMOM_% ≥Tm + ADX >ADXm + Z <+Zt
- Standard long entry on trend confirmation
- OR MEAN_REVERT regime + Z <-Zt + ADX <ADXm + TSMOM_% >0%

**WAIT**
- Conflicting signals (TSMOM and Z-score disagree)
- TRENDING_UP + TSMOM_% ≥Tm but Z >+Zt (overbought in uptrend)
- MEAN_REVERT + Z <-Zt but TSMOM_% <Tm (momentum conflict)
- CHOPPY regime + ADX <20
- TSMOM_% in range -2% to +2% (neutral/choppy momentum)

**SELL**
- TRENDING_DOWN + TSMOM_% <-2% + MA Score ≤3/7
- Exit long on downtrend confirmation
- OR MEAN_REVERT + Z >+Zt + ADX <ADXm

**STRONG SELL**
- TRENDING_DOWN + TSMOM_% <-2% + ADX >ADXm
- High conviction exit on strong downtrend
- OR Z >+(Zt+0.5) (extreme overbought)
- OR -Z(VIX) >+1.5 (complacency regime override)

---

### Position Sizing Qualifiers

**Standard Sizing (Long-Only Spot)**
- Conservative: 1x base position, strict entry criteria
- Moderate: 1x base position, balanced approach
- Aggressive: 1-1.5x base position, earlier entries allowed

**Reduced Size Scenarios**
- Lower conviction setups (0.5x)
- High volatility environments (-Z(VIX) <-1.5) (0.5x-0.75x)
- GLI contracting >2% (0.5x for high-momentum assets)

**Risk Management**
- No short positions (long-only framework)
- No leverage/margin (spot only)
- Portfolio hedging via put options when -Z(VIX) >+1.5

---

## 8. Risk Management Concepts

### Falling Knife
**Definition:** Asset in strong downtrend (ADX >25, -DI > +DI), attempting to buy at "bottom"

**Risk:** Downtrends can extend far beyond statistical oversold levels

**Framework rule:**
- Conservative/Moderate: Never buy falling knife (WAIT signal)
- Aggressive: Allow only if Z <-2.5 AND -Z(VIX) <-1.5 AND TSMOM ≥0.33 (fear regime + extreme OS + momentum stabilizing)

---

### Hedging
**Definition:** Taking offsetting positions to reduce portfolio risk.

**Implementation:** Long put options (tail risk protection)

**Triggers:**
- -Z(VIX) >+1.5 (complacency regime)
- GLI expanding + high Z-scores (frothy conditions)
- VIX <15 (cheap put premiums)

---

### Beta
**Definition:** Measure of asset's volatility relative to the market.

**Interpretation:**
- **β = 1:** Moves with market
- **β > 1:** Higher volatility (amplified moves)
- **β < 1:** Lower volatility (defensive)

**Usage:** "Risk asset beta" refers to high-beta securities sensitive to liquidity conditions

---

### Tail Risk
**Definition:** Probability of extreme loss events beyond ±3σ ("fat tail" of distribution).

**Protection:** Out-of-the-money put options provide asymmetric payoff during crashes

---

### Drawdown
**Definition:** Peak-to-trough decline during a specific period.

**Formula:**
```
Drawdown% = ((Trough - Peak) / Peak) × 100
```

---

## 9. Market Regimes

### Asset-Level Regime Classification
**Definition:** Categorization of individual asset price action based on trend, momentum, and statistical position.

**Regimes:**

| Regime | Conditions | Trading Approach |
|--------|-----------|------------------|
| **TRENDING_UP** | ADX >25, +DI > -DI, TSMOM_% >+2%, MA ≥60% | Follow trend, buy dips |
| **TRENDING_DOWN** | ADX >25, -DI > +DI, TSMOM_% <-2% | Avoid longs, wait for reversal |
| **MEAN_REVERT_BUY** | Z <-2, ADX <25, choppy trend | Oversold bounce play |
| **MEAN_REVERT_SELL** | Z >+2, ADX <25, choppy trend | Overbought fade setup |
| **CHOPPY** | ADX <20, TSMOM_% in -2% to +2% range | Avoid, no directional edge |
| **NEUTRAL** | None of the above | Monitor, no immediate action |

**Usage in framework:** Determines which signal logic to apply (trend-following vs mean-reversion)

---

### Risk-On
**Characteristics:**
- Investors favor high-beta, growth, cyclical assets
- Low VIX, tight credit spreads
- GLI expanding

**Asset performance:** Stocks, crypto, commodities outperform; bonds, USD underperform

---

### Risk-Off
**Characteristics:**
- Flight to safety
- Elevated VIX, widening spreads
- GLI contracting

**Asset performance:** Bonds, USD, gold outperform; stocks, crypto underperform

---

### Complacency
**Definition:** Extended low-volatility period (-Z(VIX) >+1.5), often precedes volatility spike.

**Action:** Trim winners, add hedges, reduce leverage

---

### Fear Regime
**Definition:** Elevated volatility and panic selling (-Z(VIX) <-1.5).

**Action:** Contrarian buying opportunity if fundamentals intact

---

## 10. Quantitative Trading Terms

### Systematic Trading
**Definition:** Rule-based approach using predefined algorithms rather than discretionary decisions.

**Characteristics:** Objective entry/exit criteria, backtestable, removes emotional bias

---

### Alpha
**Definition:** Excess return above a benchmark (market-adjusted performance).

**Formula:**
```
Alpha = Portfolio Return - (β × Market Return)
```

**"Alpha signal":** Tradable insight providing edge over passive indexing

---

### Signal-to-Noise Ratio
**Definition:** Measure of information quality vs random fluctuation.

**Application:** Higher timeframes (weekly vs daily) typically have better signal-to-noise

---

### Multi-Timeframe Analysis
**Definition:** Confirming setups across multiple periodicities (e.g., daily + weekly).

**Framework approach:** Weekly timeframe for primary signals (reduces noise)

---

### Confluence
**Definition:** Multiple independent signals/indicators pointing to same conclusion.

**Example:** Z <-2 (oversold) + ADX >25 uptrend (trend) + -Z(VIX) <-1.5 (fear) = high confluence BUY

---

### Contrarian
**Definition:** Taking positions opposite to prevailing sentiment.

**Framework application:** Buy when Fear & Greed shows Extreme Fear, sell at Extreme Greed

---

### Backtesting
**Definition:** Testing trading strategy on historical data to evaluate performance.

**Pitfalls:** Overfitting, survivorship bias, look-ahead bias

---

### Sharpe Ratio
**Definition:** Risk-adjusted return metric.

**Formula:**
```
Sharpe = (Portfolio Return - Risk-Free Rate) / σ_portfolio
```

**Interpretation:** Higher is better; >1 is good, >2 is excellent

---

## 11. Data & Sources

### FRED (Federal Reserve Economic Data)
**Source:** St. Louis Federal Reserve

**Coverage:** 800,000+ economic time series

**Framework usage:**
- `WALCL`: Fed Balance Sheet
- `WTREGEN`: Treasury General Account
- `RRPONTSYD`: Reverse Repo

---

### Yahoo Finance
**Provider:** Real-time and historical market data

**Ticker conventions:**
- US Equities: Direct symbol (`AAPL`)
- International: Exchange suffix (`ISAC.L` for London)
- Crypto: USD pair (`BTC-USD`)
- Indices: Caret prefix (`^GSPC`)
- Futures: Continuous contract (`GC=F`)

---

## 12. Statistical Distributions

### Normal Distribution (Gaussian)
**Properties:**
- Bell curve, symmetric around mean
- ~68% of data within ±1σ
- ~95% within ±2σ
- ~99.7% within ±3σ

**Assumption:** Z-score methodology assumes approximate normal distribution of returns

---

### Fat Tails (Leptokurtic Distribution)
**Definition:** Distribution with higher probability of extreme events than normal distribution predicts.

**Market reality:** Returns exhibit fat tails (crashes/rallies more frequent than Gaussian model suggests)

**Implication:** Z-score thresholds are heuristic, not absolute probability

---

## 13. Position Management

### Pyramiding
**Definition:** Adding to winning positions as they move in your favor.

**Risk:** Can amplify losses if trend reverses

**Framework:** YOLO level only (ADD TO WINNER signal)

---

### Scaling Out
**Definition:** Closing position in increments (e.g., sell 1/3 at +1σ, 1/3 at +2σ, final 1/3 at +2.5σ)

**Benefit:** Locks in partial profits while maintaining upside exposure

---

### Stop Loss
**Definition:** Predefined exit price to limit downside.

**Implementation:** Below key support, below MA, or fixed % loss threshold

---

## 14. Framework-Specific Terminology

### Zt (Z-Threshold)
**Definition:** User-selected Z-score threshold based on risk profile.

**Levels:**
- **Conservative (🥛):** ±2.0 (fewest signals, highest conviction)
- **Moderate (📊):** ±1.75 (balanced)
- **Aggressive (🌶️):** ±1.5 (more signals, earlier entries)

**Application:** Replaces fixed ±2σ rule with dynamic threshold

---

### Multi-Factor Profile Thresholds
**Definition:** Risk-specific thresholds for all indicators, not just Z-score.

**Complete Profile Matrix:**

| Profile | Z-Score | TSMOM_% | MA Score | ADX |
|---------|---------|---------|----------|-----|
| 🥛 Conservative | ±2.0 | ≥+10% | ≥6/7 | >30 |
| 📊 Moderate | ±1.75 | ≥+5% | ≥5/7 | >25 |
| 🌶️ Aggressive | ±1.5 | ≥+2% | ≥4/7 | >20 |

**Interpretation:** All thresholds must be met simultaneously for signal generation (conservative profiles require stricter conditions across all dimensions)

---

### Dual-Timeframe (Weekly/Daily)
**Framework approach:**
- **Weekly timeframe:** Primary signals using TSMOM, Z-score, MA alignment, and ADX
- **Daily timeframe:** Confirmation signals using TEMA crosses, daily Z-score, and daily ADX

**Decision Logic:**
- Weekly determines **direction** (trend/regime identification)
- Daily determines **timing** (entry/exit precision)

**Example:** Weekly shows BUY signal + Daily shows Bullish TEMA cross = STRONG BUY (highest conviction)

---

### Liquidity-Adjusted Positioning
**Concept:** Size positions based on GLI trend
- GLI expanding: Normal/aggressive sizing
- GLI contracting <-2%: Reduce momentum plays by 50%

---

## Quick Reference Tables

### Z-Score Trading Thresholds by Risk Level

| Risk Profile | Entry (OS) | Exit (OB) | Extreme |
|--------------|-----------|----------|---------|
| 🥛 Conservative | <-2.0 | >+2.0 | ±2.5 |
| 📊 Moderate | <-1.75 | >+1.75 | ±2.25 |
| 🌶️ Aggressive | <-1.5 | >+1.5 | ±2.0 |

---

### ADX Strength Guide

| ADX Range | Strength | Trading Approach |
|-----------|----------|------------------|
| 0-15 | Very Weak | Avoid directional bets, range trade |
| 15-20 | Weak | Low conviction trends, fade extremes |
| 20-25 | Moderate | Trend following acceptable with confirmation |
| 25-40 | Strong | High conviction trend trades |
| >40 | Very Strong | Pyramiding allowed, extend targets |

---

### -Z(VIX) Regime Action Matrix

| -Z(VIX) | Regime | Position Sizing | Hedge % |
|---------|--------|-----------------|---------|
| >+2.0 | Extreme Complacency | 50% normal | 20-30% |
| +1.5 to +2.0 | Complacency | 75% normal | 10-20% |
| +0.5 to +1.5 | Risk-On | 100% normal | 0-5% |
| -0.5 to +0.5 | Neutral | 100% normal | 0% |
| -1.5 to -0.5 | Risk-Off | 50-75% normal | 0% |
| <-1.5 | Fear | 100-150% (contrarian) | 0% |

---

## Acronym Index

- **ADX:** Average Directional Index
- **API:** Application Programming Interface
- **BS:** Balance Sheet
- **BTC:** Bitcoin
- **DI:** Directional Indicator (+DI, -DI)
- **EMA:** Exponential Moving Average
- **ETF:** Exchange-Traded Fund
- **ETH:** Ethereum
- **F&G:** Fear & Greed Index
- **FRED:** Federal Reserve Economic Data
- **GLI:** Global Liquidity Index
- **LLM:** Large Language Model
- **LSE:** London Stock Exchange
- **MA:** Moving Average
- **OB:** Overbought
- **OS:** Oversold
- **QE:** Quantitative Easing
- **RRP:** Reverse Repo (RRPONTSYD)
- **S&P 500:** Standard & Poor's 500 Index
- **TEMA:** Triple Exponential Moving Average
- **TGA:** Treasury General Account (WTREGEN)
- **TSMOM:** Time-Series Momentum
- **TSE:** Tokyo Stock Exchange
- **USD:** United States Dollar
- **VIX:** CBOE Volatility Index

---

## Further Reading

**Books:**
- *Quantitative Trading* - Ernest Chan
- *Evidence-Based Technical Analysis* - David Aronson
- *Trading and Exchanges* - Larry Harris

**Papers:**
- "Do Industries Explain Momentum?" - Moskowitz & Grinblatt (1999)
- "Trend Following with Managed Futures" - Hurst, Ooi, Pedersen (2013)
- "Facts and Fantasies About Commodity Futures" - Gorton & Rouwenhorst (2006)

**Resources:**
- FRED API Documentation: https://fred.stlouisfed.org/docs/api/
- Yahoo Finance API (yfinance): https://github.com/ranaroussi/yfinance
- TA-Lib Technical Indicators: https://ta-lib.org/

---

*Last updated: 2026-01-10*
