# Quantitative Finance Terminology

**Version:** 3.1.0 | Quick reference for framework indicators and signals.

---

## Core Indicators

### ZTanh
Learned z-score transformation with tanh activation. Bounded [-1, +1].

```
ZTanh = tanh(w1*Z_20 + w2*Z_50 + w3*Z_100 + w4*Z_200 + bias)
```

| Zone | Weekly | Daily |
|------|--------|-------|
| Extreme OB | > 0.85 | > 0.85 |
| Overbought | 0.75-0.85 | 0.70-0.85 |
| Upper | 0.65-0.75 | 0.50-0.70 |
| Neutral | -0.10 to 0.65 | -0.50 to 0.50 |
| Lower | -0.40 to -0.10 | -0.70 to -0.50 |
| Oversold | -0.60 to -0.40 | -0.85 to -0.70 |
| Extreme OS | < -0.60 | < -0.85 |

**Note:** Thresholds are ticker-specific (see `thresholds.json`).

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

### VIX ZTanh (Contrary Indicator)
VIX sentiment using negated weights. Positive = Greed, Negative = Fear.

| VIX ZTanh | Sentiment | Action |
|-----------|-----------|--------|
| > +0.70 | Extreme Greed | Trim, add hedges |
| +0.50 to +0.70 | Greed | Caution on buys |
| +0.20 to +0.50 | Mild Greed | Normal |
| -0.20 to +0.20 | Neutral | Standard ops |
| -0.50 to -0.20 | Mild Fear | Pullback opportunity |
| -0.70 to -0.50 | Fear | Contrarian buy |
| < -0.70 | Extreme Fear | Strong contrarian buy |

---

### GLI (Global Liquidity Index)
Net Fed liquidity: `GLI = Fed BS - TGA - RRP`

| Component | FRED Code | Description |
|-----------|-----------|-------------|
| Fed BS | WALCL | Fed total assets |
| TGA | WTREGEN | Treasury cash account |
| RRP | RRPONTSYD | Reverse repo (parked cash) |

| GLI 4w Change | Signal |
|---------------|--------|
| > +1% | Expanding (risk-on) |
| < -1% | Contracting (risk-off) |
| < -2% | Override: downgrade BUYs |

---

## Regime Classification

| Regime | Conditions | Mode |
|--------|------------|------|
| TRENDING_UP | ADX >25 + TSMOM >2% + MA ≥60% | Trend-follow: long |
| TRENDING_DOWN | ADX >25 + TSMOM <-2% | Trend-follow: exit |
| TREND_UNCLEAR | ADX >25 + mixed signals | Trend present, mixed |
| TREND_EMERGING_UP | ADX 20-25 + TSMOM >2% | Cautious long |
| TREND_EMERGING_DOWN | ADX 20-25 + TSMOM <-2% | Cautious exit |
| MEAN_REVERT_BUY | ADX <20 + ZTanh ≤ oversold | Mean-reversion: long |
| MEAN_REVERT_SELL | ADX <20 + ZTanh ≥ overbought | Mean-reversion: short |
| CHOPPY | ADX <20 + no extreme ZTanh | No-trade mode |
| NEUTRAL | ADX 20-25 + TSMOM neutral | No clear edge |

---

## Risk Profiles

| Profile | ZTanh | TSMOM | MA Score | ADX |
|---------|-------|-------|----------|-----|
| Conservative | ±0.75 | ≥+10% | ≥6/7 | >30 |
| Moderate | ±0.60 | ≥+5% | ≥5/7 | >25 |
| Aggressive | ±0.50 | ≥+2% | ≥4/7 | >20 |

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

### ADX + ZTanh Matrix
| ADX | ZTanh | Action |
|-----|-------|--------|
| >25 | <-0.40 | BUY THE DIP |
| >25 | >+0.75 | SELL THE TOP |
| <20 | <-0.50 | Mean-reversion BUY |
| <20 | >+0.50 | Mean-reversion SELL |
| 20-25 | Neutral | WAIT |

### VIX Level + VIX ZTanh
| VIX | VIX ZTanh | State |
|-----|-----------|-------|
| <15 | >+0.50 | Extreme complacency |
| 15-20 | neutral | Normal |
| 20-30 | <-0.50 | Elevated fear |
| >30 | <-0.70 | Panic (contrarian buy) |

---

## Acronyms

| Acronym | Meaning |
|---------|---------|
| ADX | Average Directional Index |
| DI | Directional Indicator |
| GLI | Global Liquidity Index |
| MA | Moving Average |
| OB/OS | Overbought/Oversold |
| RRP | Reverse Repo |
| TGA | Treasury General Account |
| TSMOM | Time-Series Momentum |
| VIX | CBOE Volatility Index |
| ZTanh | Z-score with tanh activation |

---

*Last updated: 2026-01-19*
