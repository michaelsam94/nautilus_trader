# VectorBT Template Ports

Signal logic extracted from [marketcalls/vectorbt-backtesting-skills](https://github.com/marketcalls/vectorbt-backtesting-skills) templates.

Source clone: `.vectorbt-skills-source/`

## Summary

| Metric | Count |
|--------|------:|
| Templates | 12 |
| Ported | 4 |
| Dedup skipped | 2 |
| Blocked | 6 |

## Ported

| Template | Module |
|----------|--------|
| donchian | `donchian_breakout.DonchianBreakout` |
| rsi | `rsi_threshold.RsiThreshold` |
| supertrend | `supertrend.SupertrendCross` |
| momentum | `double_momentum.DoubleMomentum` |

## Dedup skipped

| Template | Duplicate of |
|----------|--------------|
| ema_crossover | `freqtrade_ported.average_strategy.AverageStrategy` |
| macd | `freqtrade_ported.macd_strategy.MacdStrategy` |

OpenAlgo/vectorbt backtest harness code is not ported — only entry/exit rules.
