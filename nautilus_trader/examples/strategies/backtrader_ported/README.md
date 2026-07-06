# Backtrader Strategy Ports

Ports from [ali-azary/Algorithmic-Trading-From-Beginner-to-Advanced](https://github.com/ali-azary/Algorithmic-Trading-From-Beginner-to-Advanced) `codes/`.

Source clone: `.backtrader-ali-source/`

## Summary

| Metric | Count |
|--------|------:|
| Upstream strategies | 11 |
| Ported (long-only) | 3 |
| Blocked | 8 |

## Ported

| Source file | Module | Notes |
|-------------|--------|-------|
| KeltnerBreakoutStrategy.py | `keltner_breakout.KeltnerBreakout` | Long only |
| RelativeMomentumAccel.py | `relative_momentum_accel.RelativeMomentumAccel` | ATR stop → mean exit |
| MomentumIgnitionStrategy.py | `momentum_ignition.MomentumIgnition` | Long only |

yfinance runners and matplotlib from upstream are not ported.
