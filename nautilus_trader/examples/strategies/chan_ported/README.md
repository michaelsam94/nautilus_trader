# Chan (2013) Strategy Ports

Ports of trading strategies from Ernest Chan, *Algorithmic Trading: Winning Strategies and Their Rationale* (Wiley, 2013).

**Source PDF:** `Algorithmic Trading - Winning Strategies and Their Rationale 2013.pdf`

## Catalog summary

Run `catalog_summary()` from `chan_ported.catalog` for live counts. As of extraction:

| Status | Count | Meaning |
|--------|------:|---------|
| `ported` | 15 | Full Nautilus strategy module |
| `partial` | 1 | Single-asset proxy for multi-asset book strategy |
| `dedup_skip` | 9 | Covered by another port folder |
| `blocked` | 8 | Needs options, tick, universe, or event data |
| `methodology` | 11 | Tests, sizing, risk — not standalone alpha |

**Book strategy concepts catalogued:** 44  
**Nautilus modules implemented:** 16 (15 ported + 1 partial)

## Book chapter → Nautilus mapping

| Chapter | Topic | Port module |
|---------|-------|-------------|
| 2 | Linear mean reversion (USD.CAD) | `linear_mean_reversion` |
| 2 | Johansen 3-ETF portfolio MR | `johansen_portfolio_mr` |
| 3 | Price / log / ratio spread pairs | `linear_spread_pairs`, `log_spread_pairs`, `ratio_spread_pairs` |
| 3 | Bollinger spread MR | `bollinger_spread_pairs` |
| 3 | Kalman dynamic hedge pairs | `kalman_pairs` |
| 4 | Buy-on-gap intraday MR | `buy_on_gap` |
| 4 | Cross-sectional MR | `cross_sectional_mean_reversion` (partial) |
| 5 | Currency z-score MR | `currency_zscore_mr` |
| 5 | Vol vs equity intermarket | `vol_equity_spread` |
| 6 | Futures TSMOM + hold days | `futures_tsmom_staggered` |
| 7 | Opening gap momentum | `opening_gap_momentum` |
| 7 | Leveraged ETF rebalance | `leveraged_etf_rebalance` |

## Dedup vs existing ports

See `dedup.py` and `catalog.py` `dedup_target` fields. Key overlaps:

- **Pair z-score:** `systematic_trading_ported.pair_trading` — Chan linear/Bollinger/Kalman spread variants ported separately.
- **TSMOM:** `academic_ported.time_series_momentum` — Chan staggered hold in `futures_tsmom_staggered`.
- **Cross-sectional momentum:** `academic_ported.cross_sectional_momentum` — dedup skipped.
- **Country ETF pairs:** `academic_ported.country_etf_pairs` — dedup skipped.
- **OU MR:** `backtrader_ported.ou_mean_reversion` — different model from Chan linear z-score.

## Blocked strategies

| Strategy | Reason |
|----------|--------|
| ETF component arbitrage (Ex 4.2) | Full constituent basket |
| Calendar spread MR (Ex 5.4) | Multi-contract futures γ series |
| Futures vs ETF roll arb (Ch 6) | Simultaneous curve + ETF data |
| PEAD (Ex 7.2) | Earnings announcement calendar |
| News sentiment / fund flows | Alternative data feeds |
| Kalman market making (Ch 3) | Tick / LOB data |
| High-frequency (Ch 7) | Sub-second execution |

## Conventions

- Single-asset strategies extend `freqtrade_ported.base.FreqtradeLongOnlyStrategy`.
- Two-leg spreads extend `chan_ported.base.ChanPairSpreadStrategy`.
- Chan-specific indicators live in `indicators.py` (Kalman hedge, spread z-score, half-life helper).

## Usage

```python
from nautilus_trader.examples.strategies.chan_ported import (
    KalmanPairs,
    KalmanPairsConfig,
    catalog_summary,
)

print(catalog_summary())
```
