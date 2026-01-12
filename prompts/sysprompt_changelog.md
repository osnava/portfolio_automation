# SYSPROMPT.MD Changelog

## v2.5.0 - 2026-01-12
- **MAJOR RESTRUCTURE** - Optimized for LLM with extended thinking enabled
- **Eliminated redundancy** - Removed duplicate signal definitions (previously in 3 locations)
- **Consolidated position sizing** - Single table replacing 3 verbose text blocks (Conservative/Moderate/Aggressive)
- **Reordered sections** - Logical flow: Input → Thresholds → Signal Logic → Overrides → Output
- **Converted templates to principles** - OSCASH commentary now principle-based (7 numbered guidelines) vs rigid template with brackets
- **Moved examples to end** - Reference section at bottom (watchlist scenarios, signal strength, regime examples)
- **Condensed tables** - Removed verbose TSMOM Reference and Regime Context tables (LLM can interpolate from thresholds)
- **Streamlined verification** - Reduced Sanity Check from detailed checklist to 7-point verification (trusting extended thinking)
- **~39% reduction** - From 375 lines to 227 lines while maintaining all logic
- **Improved scannability** - Clear section breaks, consolidated rules, principle-based guidance

## v2.4.0 - 2026-01-12
- **Revised Signal Taxonomy** - Replaced generic signals with explicit action types
- New signals: BUY (momentum), BUY THE DIP (mean-reversion), SELL (downtrend), SELL THE TOP (take profits), WAIT (no edge)
- **Redefined WATCHLIST Logic** - Changed from "oversold but fails thresholds" to "weekly confirmed, daily timing not optimal"
- Watchlist now monitors assets with weekly conviction (BUY/SELL signals) waiting for optimal daily entry
- Updated WATCHLIST INCLUSION CRITERIA with 3 concrete examples (weekly-daily divergence scenarios)
- **Removed RISK TRIGGERS Section** - Deleted from OSCR commentary (risks implicit in signal design)
- **Updated CONVICTION PLAYS** - Now references BUY/BUY THE DIP signal types explicitly
- **Updated EXITS/TRIMS** - Now references SELL/SELL THE TOP signal types explicitly
- **Key Drivers Column** - Clarified guidance to explain optimal entry when daily not aligned with weekly
- Signal rules table updated with new signal types mapped to regime conditions

## v2.3.1 - 2026-01-12
- **Added WATCHLIST INCLUSION CRITERIA** - Explicit rules for watchlist candidates
- Watchlist requires: Z < -Zt (oversold) + fails TSMOM/ADX thresholds + not falling knife
- Added 3 concrete examples showing watchlist vs BUY distinction
- Updated WATCHLIST section in commentary template with clearer criteria

## v2.3.0 - 2026-01-12
- **Revised OSCASH Commentary** - Completely rewritten for conciseness and directness
- Reduced from 300 words to 150-200 words target
- Removed character "OSCR", replaced with direct market analysis format
- Added explicit WAIT signal handling (when 70%+ or 100% signals are WAIT)
- Streamlined sections: Regime → Thesis → Conviction → Exits → Watchlist → Actionable → Risk → Final
- Stronger, more direct language: "Cash is a position" not "consider waiting"
- Removed examples and verbose explanations
- Added "WAIT SIGNAL GUIDANCE" for preservation mode messaging
- Emphasis on metrics-first, narrative-second approach

## v2.2.1 - 2026-01-12
- **Streamlined Daily Sheet** - Reduced from 21 to 12 columns (~43% cleaner)
- Removed redundant columns: Z-Score_Zone, TEMA20/50/200 absolute values, TEMA_Alignment, Trend_Daily
- Consolidated TEMA_Dist into single formatted column (e.g., "20:+2.3% | 50:+5.1% | 200:+8.9%")
- Consolidated Crosses into single column (e.g., "20x50:Bullish | 50x200:None")
- Renamed columns for clarity: Z-Score_Daily→Z-Score, ADX_Daily→ADX, TEMA_Consensus→Consensus, TEMA_Confidence→Confidence
- Updated conditional formatting to match new column positions
- Fixed conditional formatting error for Crosses column
- Updated Daily Confirmation workflow to reference new column names
- Updated position sizing sections to use "Confidence" column name consistently

## v2.2.0 - 2026-01-12
- **NEW: Multi-Period TEMA Ensemble** - Calculates TEMA signals across 3 period sets (fast/standard/slow)
- **NEW: Volatility-Adaptive Periods** - Automatically adjusts TEMA periods based on current market volatility
- **NEW: TEMA_Consensus column** - Signal strength from -1.0 (bearish) to +1.0 (bullish)
- **NEW: TEMA_Confidence column** - Agreement level from 0.0 to 1.0 (quality filter)
- **NEW: TEMA_Ensemble column** - Shows period agreement (e.g., "3/3", "2/3")
- **NEW: Trend_Ensemble column** - Enhanced trend classification using ensemble
- **NEW: Vol_Scalar column** - Current volatility vs historical (affects period selection)
- Added position sizing guidance by confidence tier for all risk profiles
- Updated Daily Confirmation workflow to prioritize confidence metrics

## v2.1.0 - 2026-01-11
- Added Name column to all sheet descriptions (Weekly, Momentum, Daily)
- Updated Table 2 (Ticker Signals) to include Name column
- Updated Table 3 (Rebalance Actions) format to "Name (TICKER)"
- Updated OSCASH commentary template to use "Name (TICKER)" format throughout
- Improved readability with full company names alongside ticker symbols

## v2.0.0 - [Previous date]
- Initial structured version with OSCASH Markets commentary
- Multi-profile risk system (Conservative, Moderate, Aggressive)
- Weekly + Daily confirmation workflow
- TEMA-based daily signals
