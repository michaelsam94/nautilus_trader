# Gekko Strategy Ports

Bar-signal logic ported from [xFFFFF/Gekko-Strategies](https://github.com/xFFFFF/Gekko-Strategies),
discovered via [SpiralDevelopment/Awesome-Crypto-Trading](https://github.com/SpiralDevelopment/Awesome-Crypto-Trading)
(the awesome list itself contains no code — this is its only linked strategy collection
not already covered by other `*_ported` packages).

Source clone: `.gekko-strategies-source/`

## Summary

| Metric | Count |
|--------|------:|
| Source JS files | 612 |
| Distinct strategy families | ~19 |
| Ported | 5 |
| Dedup skipped | 8 families |
| Blocked | 4 families (NN/GA/deferred/personal packs) |

## Ported

| Source | Module | Notes |
|--------|--------|-------|
| RSI_BULL_BEAR | `rsi_bull_bear.RsiBullBear` | Flagship Gekko strategy (Tommie Hansen) |
| RSI_BULL_BEAR_ADX | `rsi_bull_bear_adx.RsiBullBearAdx` | ADX modifier applied as documented (JS bug fixed) |
| NEO | `neo.Neo` | Triple-RSI, ROC idle-bull split |
| BodhiDI_public | `bodhi_di.BodhiDi` | Pure DI flipper |
| buyatsellat | `buy_at_sell_at.BuyAtSellAt` | Mechanical percent flipper |

Gekko `long`/`short` advice maps to long/flat (spot semantics) on the
`FreqtradeLongOnlyStrategy` base. Defaults come from each strategy's shipped
`.toml`.

## Dedup / blocked

See `catalog.py` for the full family-level mapping. Headline duplicates: BBRSI,
CCI, MACD, EMA/DEMA/TEMA crossovers, SuperTrend, Ichimoku — all already ported in
`freqtrade_ported`, `vectorbt_ported`, or `backtrader_ported`. Neural-net and
genetic-algorithm folders are not portable as deterministic bar logic.

## Other Awesome-Crypto-Trading links (no port value)

Frameworks (ccxt, backtrader, zipline, Lean, catalyst), arbitrage/market-making
bots (blackbird, peregrine, triangle-arb, tribeca, kelp, DEXBot), and repos
already catalogued in `STRATEGY_SOURCES.md` (je-suis-tm/quant-trading,
hummingbot, awesome-quant lists, Gekko/zenbot frameworks).
