# Jesse Strategy Ports

Ports of [jesse-ai/example-strategies](https://github.com/jesse-ai/example-strategies) to Nautilus Trader.

**Examples only — not intended for live trading.**

## Summary

| Metric | Count |
|--------|------:|
| Upstream strategies | 12 |
| Ported | 7 |
| Partial | 2 (`TurtleRules`, `IFR2`) |
| Dedup skipped | 2 |
| Blocked | 2 |

Source clone: `.jesse-source/`

All strategies reuse `freqtrade_ported.base.FreqtradeLongOnlyStrategy` (Jesse `should_long` / `update_position` → `check_entry` / `check_exit` or custom `on_bar`).

## Ported modules

| Jesse folder | Nautilus module |
|--------------|-----------------|
| Donchian | `donchian_sma200.DonchianSma200` |
| RSI2 | `rsi2.Rsi2` |
| MACD_EMA | `macd_ema.MacdEma` |
| SimpleBollinger | `simple_bollinger.SimpleBollingerIchimoku` |
| TurtleRules | `turtle_rules.TurtleRulesLong` |
| TradingView_RSI | `tradingview_rsi.TradingViewRsi` |
| IFR2 | `ifr2.Ifr2` |

## Dedup skipped

| Source | Duplicate of |
|--------|--------------|
| SMACrossover | `freqtrade_ported.average_strategy.AverageStrategy` |
| DUAL_THRUST | `systematic_trading_ported.dual_thrust.DualThrust` |

See `dedup.py` and `catalog.py` for full status.
