# Academic Strategy Ports

Catalog and selective ports from [paperswithbacktest/awesome-systematic-trading](https://github.com/paperswithbacktest/awesome-systematic-trading) `static/strategies/`.

Source clone: `.papers-source/`

## Summary

| Metric | Count |
|--------|------:|
| Upstream QC scripts | 59 |
| Ported (simplified) | 1 |
| Blocked (universe/factor) | 58 |

Most upstream files are QuantConnect `QCAlgorithm` scripts with universe selection, fundamentals, or multi-asset rotation — not portable as single-instrument bar strategies without a portfolio layer.

## Ported

| Source | Module | Notes |
|--------|--------|-------|
| time-series-momentum-effect.py | `time_series_momentum.TimeSeriesMomentum` | Single-asset ROC sign vs 58-asset QC original |

See `catalog.py` for per-file blocked reasons.
