# Quantitative Finance Terminology

**Version:** 4.0.0 | Quick reference for framework indicators and signals.

---

## Core Indicators

### RSI (Relative Strength Index)
14-period momentum oscillator. Range: 0-100.

| RSI | Zone | Interpretation |
|-----|------|----------------|
| > 70 | Overbought | Potential reversal down |
| 30-70 | Neutral | No extreme reading |
| < 30 | Oversold | Potential reversal up |

**Parameters:** Period = 14 (standard)

---

### Bollinger Bands
20-period moving average with standard deviation bands at 1, 2, 3 STD.

| Position | Condition | Interpretation |
|----------|-----------|----------------|
| Above +3 STD | Price > Upper 3 | Extreme overbought |
| Above +2 STD | Price > Upper 2 | Overbought |
| Above +1 STD | Price > Upper 1 | Above average |
| Within Bands | Between -1 and +1 | Normal range |
| Below -1 STD | Price < Lower 1 | Below average |
| Below -2 STD | Price < Lower 2 | Oversold |
| Below -3 STD | Price < Lower 3 | Extreme oversold |

**Parameters:** Period = 20, STD levels = 1, 2, 3

---

### TSMOM (Time-Series Momentum)
Average percentage return across 4w, 12w, 26w lookbacks.

```
TSMOM_% = (R_4w + R_12w + R_26w) / 3
```

| TSMOM | Interpretation |
|-------|----------------|
| > +15% | Strong momentum |
| +5% to +15% | Moderate |
| +2% to +5% | Weak positive |
| -2% to +2% | Neutral (WAIT) |
| < -5% | Strong negative |

---

### ADX (Average Directional Index)
Trend strength indicator. Range: 0-100.

| ADX | Interpretation | Action |
|-----|----------------|--------|
| < 20 | No trend | Mean-reversion mode |
| 20-25 | Emerging | Cautious trend-following |
| 25-40 | Trending | Follow trend |
| > 40 | Strong | Watch for reversal |

**Periods:** Daily = 14, Weekly = 21

**DI Bias:** +DI > -DI = Bullish, -DI > +DI = Bearish

---

### MA Score (0-7)
Moving average alignment score.

| Check | Condition |
|-------|-----------|
| 1 | Price > MA20 |
| 2 | Price > MA50 |
| 3 | Price > MA100 |
| 4 | Price > MA200 |
| 5 | MA20 > MA50 |
| 6 | MA50 > MA100 |
| 7 | MA100 > MA200 |

| Score | Structure |
|-------|-----------|
| 7/7 | Strong uptrend |
| 5-6/7 | Uptrend |
| 3-4/7 | Mixed |
| 0-2/7 | Downtrend |

---

### VIX RSI (Contrary Indicator)
VIX sentiment using RSI. High RSI = High VIX = Fear = BUY opportunity.

| VIX RSI | Sentiment | Action |
|---------|-----------|--------|
| > 80 | Extreme Fear | Strong contrarian buy |
| 70-80 | Fear | Contrarian buy |
| 60-70 | Mild Fear | Pullback opportunity |
| 40-60 | Neutral | Standard ops |
| 30-40 | Mild Greed | Caution |
| 20-30 | Greed | Trim longs |
| < 20 | Extreme Greed | High caution |

---

### KAMA (Kaufman's Adaptive Moving Average)
Adaptive MA that adjusts to market noise. Used as trend filter on daily.

**Parameters:** window=10, fast=2, slow=30

| Price_vs_KAMA | Condition | Action |
|---------------|-----------|--------|
| Extended Above | > KAMA + 2% | Wait for pullback |
| Above | > KAMA | Trend intact, ok to enter |
| Below | < KAMA | Trend weak, caution |
| Extended Below | < KAMA - 2% | Oversold bounce possible |

**Key Rule:** RSI Oversold + Price > KAMA = BUY. RSI Oversold + Price < KAMA = WAIT.

---

### GLI (Global Liquidity Index)
Global central bank liquidity aggregated from Fed, ECB, BOJ balance sheets + broad money (M2/M3) across 12 economies.

**Formula:**
```
Net_Fed = FED_BS - TGA - RRP
GLI = Net_Fed + ECB_BS_USD + BOJ_BS_USD + Global_Broad_Money
```

**Central Bank Balance Sheets:**

| Component | FRED Code | Currency | Frequency |
|-----------|-----------|----------|-----------|
| Fed BS | WALCL | USD | Weekly |
| TGA | WTREGEN | USD | Weekly |
| RRP | RRPONTSYD | USD | Daily |
| ECB BS | ECBASSETSW | EUR | Weekly |
| BOJ BS | JPNASSETS | JPY | Monthly |

**Broad Money (12 economies):**

| Economy | FRED Code | Type | Currency |
|---------|-----------|------|----------|
| USA | M2SL | M2 | USD |
| Eurozone | MABMM301EZM189N | M3 | EUR |
| Japan | MABMM301JPM189S | M3 | JPY |
| China | MYAGM2CNM189N | M2 | CNY |
| UK | MABMM301GBM189N | M3 | GBP |
| Canada | MABMM301CAM189N | M3 | CAD |
| Australia | MABMM301AUM189N | M3 | AUD |
| India | MABMM301INM189N | M3 | INR |
| Switzerland | MABMM301CHM189N | M3 | CHF |
| Brazil | MABMM301BRM189N | M3 | BRL |
| S. Korea | MABMM301KRM189S | M3 | KRW |
| Mexico | MABMM301MXM189N | M3 | MXN |

**Note:** FRED's non-US broad money series lag by months/years. The absolute GLI value will undercount vs. TradingView's GLI (~15-20%), but trend/momentum signals (WoW, MoM, QoQ) remain valid for directional analysis.

**FX Conversion:** 11 FRED FX pairs (DEXUSEU, DEXJPUS, DEXCHUS, DEXUSUK, DEXCAUS, DEXUSAL, DEXINUS, DEXSZUS, DEXBZUS, DEXKOUS, DEXMXUS).

| GLI 4w Change | Signal |
|---------------|--------|
| > +1% | Expanding (risk-on) |
| < -1% | Contracting (risk-off) |
| < -2% | Override: downgrade BUYs |

**Lagged GLI (10w ago):** Markets follow liquidity with ~10 week delay. The "10w ago" value shows liquidity conditions that are now affecting prices. Used for prose context, not mechanical signals.

**Fallback:** If global data unavailable, reverts to US-only (Net Fed).

---

## Regime Classification

| Regime | Conditions | Mode |
|--------|------------|------|
| Trending Up | ADX >25 + TSMOM >2% | Trend-follow: long |
| Trending Down | ADX >25 + TSMOM <-2% | Trend-follow: exit |
| Trend Unclear | ADX >25 + TSMOM neutral | Trend present, signals mixed |
| Emerging Up | ADX 20-25 + TSMOM >2% | Cautious long |
| Emerging Down | ADX 20-25 + TSMOM <-2% | Cautious exit |
| Mean Revert Buy | ADX <20 + RSI <= 30 | Mean-reversion: long |
| Mean Revert Sell | ADX <20 + RSI >= 70 | Mean-reversion: short |
| Choppy | ADX <20 + RSI neutral | No-trade mode |
| Neutral | ADX 20-25 + TSMOM neutral | No clear edge |

---

## Risk Profiles

| Profile | RSI | TSMOM | ADX |
|---------|-----|-------|-----|
| Conservative | <=25 / >=75 | >=+10% | >30 |
| Moderate | <=30 / >=70 | >=+5% | >25 |
| Aggressive | <=35 / >=65 | >=+2% | >20 |

---

## Signals

| Signal | Meaning |
|--------|---------|
| BUY | Enter long (trend-following) |
| BUY THE DIP | Enter long (oversold in uptrend) |
| SELL | Exit long (trend-following) |
| SELL THE TOP | Exit long (overbought) |
| WAIT | No action (conflicting signals) |

**Daily Entry Signals:**
| Entry | Meaning |
|-------|---------|
| EXECUTE | Proceed with weekly signal |
| WAIT FOR PULLBACK | Daily extended, wait |
| WAIT FOR CONFIRMATION | Daily DI not aligned |
| WATCHLIST | Monitor for entry |

---

## Quick Reference

### ADX + RSI Matrix
| ADX | RSI | Action |
|-----|-----|--------|
| >25 | <30 | BUY THE DIP |
| >25 | >70 | SELL THE TOP |
| <20 | <30 | Mean-reversion BUY |
| <20 | >70 | Mean-reversion SELL |
| 20-25 | 30-70 | WAIT |

### VIX Level + VIX RSI
| VIX | VIX RSI | State |
|-----|---------|-------|
| <15 | <30 | Extreme complacency |
| 15-20 | 40-60 | Normal |
| 20-30 | 60-80 | Elevated fear |
| >30 | >80 | Panic (contrarian buy) |

---

## Acronyms

| Acronym | Meaning |
|---------|---------|
| ADX | Average Directional Index |
| BB | Bollinger Bands |
| DI | Directional Indicator |
| GLI | Global Liquidity Index |
| KAMA | Kaufman's Adaptive Moving Average |
| MA | Moving Average |
| OB/OS | Overbought/Oversold |
| RRP | Reverse Repo |
| RSI | Relative Strength Index |
| STD | Standard Deviation |
| TGA | Treasury General Account |
| TSMOM | Time-Series Momentum |
| VIX | CBOE Volatility Index |

---

*Last updated: 2026-01-29*
