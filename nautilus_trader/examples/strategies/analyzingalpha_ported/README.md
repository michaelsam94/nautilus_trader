# analyzingalpha Strategy Ports

Bar-signal logic ported from [leosmigel/analyzingalpha](https://github.com/leosmigel/analyzingalpha),
discovered via [wangzhe3224/awesome-systematic-trading](https://github.com/wangzhe3224/awesome-systematic-trading).

That awesome list links 243 GitHub repos, almost all libraries/frameworks/data
tools. Its strategy-code sources: je-suis-tm/quant-trading (already fully ported
as `systematic_trading_ported/`), this repo, and
[chrisconlan/algorithmic-trading-with-python](https://github.com/chrisconlan/algorithmic-trading-with-python)
(examined — both of its signals are duplicates; see `catalog.py`). The rest are
catalogued as blocked/hard in `STRATEGY_SOURCES.md` (PyTrendFollow,
QuantsPlaybook, fmzquant, czsc, pysystemtrade, ML/RL repos).

Source clones: `.analyzingalpha-source/` (note: strategy `.py` files are
git-LFS pointers; fetch via `media.githubusercontent.com`), `.conlan-source/`

## Summary

| Metric | Count |
|--------|------:|
| Strategy sources found | 13 (incl. 2 conlan signals) |
| Ported | 3 |
| Dedup skipped | 6 |
| Blocked | 4 |

## Ported

| Source | Module | Notes |
|--------|--------|-------|
| ConnorsRSI (Backtrader) | `connors_rsi.ConnorsRsi` | Composite RSI(3)+streak-RSI(2)+PercentRank(100); ≤10 in, ≥90 out |
| Price shear (notebook) | `price_shear.PriceShear` | 2.5×ATR displacement below EMA12; one-bar hold |
| Slingshot (notebook) | `slingshot.Slingshot` | Daily SMA50 trend + EMA10 pullback, intraday EMA4-of-highs trigger, stop at daily low, 2R target |

`Slingshot` is multi-timeframe: set `bar_type` to the trigger timeframe and
`daily_bar_type` to the context timeframe (1h/1d in the source).
