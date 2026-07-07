# Trading Strategy Source Catalog

Research catalog of GitHub repositories and curated lists containing large collections of trading strategies, for prioritizing ports into `nautilus_trader/examples/strategies/`.

**Research date:** 2026-07-06  
**Already ported in this repo:**

| Package | Source | Ported | Notes |
|---------|--------|-------:|-------|
| `freqtrade_ported/` | [freqtrade/freqtrade-strategies](https://github.com/freqtrade/freqtrade-strategies) | 22 / 65 | 19 full + 3 partial; see `freqtrade_ported/catalog.py` |
| `systematic_trading_ported/` | [wangzhe3224/awesome-systematic-trading](https://github.com/wangzhe3224/awesome-systematic-trading) → [je-suis-tm/quant-trading](https://github.com/je-suis-tm/quant-trading) | 7 / 15 TA | 2 dedup-skipped; 5 quantamental blocked |
| `jesse_ported/` | [jesse-ai/example-strategies](https://github.com/jesse-ai/example-strategies) | 8 / 12 | 2 dedup-skipped; MAGen partial (fixed defaults) |
| `vectorbt_ported/` | [marketcalls/vectorbt-backtesting-skills](https://github.com/marketcalls/vectorbt-backtesting-skills) | 6 / 12 | Signal logic; 2 dedup-skipped; 1 partial (rsi_accumulation) |
| `backtrader_ported/` | [ali-azary/Algorithmic-Trading-From-Beginner-to-Advanced](https://github.com/ali-azary/Algorithmic-Trading-From-Beginner-to-Advanced) | 3 / 11 full + 8 partial | Long-only subsets |
| `quant_algos_ported/` | [Astralchemist/Quant-Algos](https://github.com/Astralchemist/Quant-Algos) | 0 / ~311 | Scaffold placeholders; dedup catalog only |
| `academic_ported/` | [paperswithbacktest/awesome-systematic-trading](https://github.com/paperswithbacktest/awesome-systematic-trading) `static/strategies/` | 1 / 59 | QC universe scripts; 58 blocked |
| `gekko_ported/` | [SpiralDevelopment/Awesome-Crypto-Trading](https://github.com/SpiralDevelopment/Awesome-Crypto-Trading) → [xFFFFF/Gekko-Strategies](https://github.com/xFFFFF/Gekko-Strategies) | 5 / ~19 families | 612 JS files collapse to ~19 families; NN/GA blocked; see `gekko_ported/catalog.py` |
| `analyzingalpha_ported/` | [wangzhe3224/awesome-systematic-trading](https://github.com/wangzhe3224/awesome-systematic-trading) → [leosmigel/analyzingalpha](https://github.com/leosmigel/analyzingalpha) | 3 / 13 | + chrisconlan/algorithmic-trading-with-python fully dedup-skipped; see `analyzingalpha_ported/catalog.py` |

---

## Executive Summary

We catalogued **52 repositories and meta-sources** across Freqtrade, Jesse, Backtrader, QuantConnect/Lean, vectorbt, awesome lists, exchange-specific bots, and quant-fund style projects.

**Highest port value (unique, runnable Python bar/signal logic):**

1. **Remaining `freqtrade/freqtrade-strategies`** (~47 not yet ported) — same `FreqtradeLongOnlyStrategy` pipeline already exists.
2. **`paperswithbacktest/awesome-systematic-trading`** — **180** vendored QuantConnect-style academic strategy scripts (unique factor/rotation logic).
3. **`jesse-ai/example-strategies`** — **12** clean Jesse examples (crypto-native, medium port effort).
4. **`ali-azary/Algorithmic-Trading-From-Beginner-to-Advanced`** — **11** Backtrader strategies with yfinance runners.
5. **`Astralchemist/Quant-Algos`** — **~311** Python files across 15+ strategy categories (curate; quality varies).

**Large but heavy dedup / low incremental value:**

- `keithorange/HUGE_FreqTrade_Strategy_Collection` (**478** `.py`) — scraped Freqtrade dump; mostly overlaps official + community repos.
- `davidzr/freqtrade-strategies` (**465** `.py`) — NFI family + forks; massive overlap with official catalog.
- `fmzquant/strategies` (**~5,800** FMZ links) — link catalog, multi-language, FMZ-runtime-specific.

**Meta-aggregator (not a repo):** [Freqtrade Strategies Hub](https://fts.naif.one/) indexes **~12,900** public strategies across **~1,000** GitHub repos — useful for discovery, not bulk porting.

**Portability legend**

| Rating | Meaning |
|--------|---------|
| **Easy** | Single-instrument, bar-based, indicators already in `freqtrade_ported/indicators.py` |
| **Medium** | Different framework API but straightforward signal logic (Jesse, Backtrader, quant-trading pandas) |
| **Hard** | Multi-asset, portfolio weights, options, ML/DRL, custom runtime (FMZ, Lean universes, agent stacks) |

---

## Tier 1 — Large Code Repos (50+ strategies)

| Repo | ~Count | Format | Maintenance | Overlap w/ ported | Portability | Code vs catalog |
|------|-------:|--------|-------------|-------------------|-------------|-----------------|
| [keithorange/HUGE_FreqTrade_Strategy_Collection](https://github.com/keithorange/HUGE_FreqTrade_Strategy_Collection) | 478 | Freqtrade `IStrategy` | Stale (2024-04) | **High** — superset of official + community | Easy–medium (per file) | Code |
| [davidzr/freqtrade-strategies](https://github.com/davidzr/freqtrade-strategies) | 465 | Freqtrade `IStrategy` | Low activity (2024-02) | **High** — includes NFI variants, duplicates berlinguyinca set | Easy–medium | Code |
| [QuantConnect/Lean](https://github.com/QuantConnect/Lean) `Algorithm.Python/` | 427 | `QCAlgorithm` (Python) | **Active** (daily) | Low — equities/futures/options focus | **Hard** | Code |
| [Astralchemist/Quant-Algos](https://github.com/Astralchemist/Quant-Algos) | ~311 | Plain Python / framework-agnostic folders | Active (2026) | Low–medium — some classic TA overlaps | Medium | Code |
| [paperswithbacktest/awesome-systematic-trading](https://github.com/paperswithbacktest/awesome-systematic-trading) `static/strategies/` | 180 | QuantConnect `QCAlgorithm` scripts | Moderate (2025-01) | Low — academic factor/rotation | **Hard** | **Hybrid** (list + code) |
| [hugo2046/QuantsPlaybook](https://github.com/hugo2046/QuantsPlaybook) | 100+ | Jupyter notebooks + Python (A-share quant research) | **Active** (2026) | Low — China equity factor/timing | **Hard** (notebooks, CN market) | Code |
| [fmzquant/strategies](https://github.com/fmzquant/strategies) | ~5,800 links | JS/Python/C++/Pine/Blockly/MyLanguage | Catalog updated (2025-04) | Medium for TA names | **Hard** (FMZ runtime) | **Link catalog** |
| [werkkrew/freqtrade-strategies](https://github.com/werkkrew/freqtrade-strategies) | 122 | Freqtrade `IStrategy` | **Stale** (2021) | High | Easy–medium | Code |
| [jesse-ai/jesse](https://github.com/jesse-ai/jesse) `jesse/strategies/` | ~145 | Jesse `Strategy` (+ many test fixtures) | **Active** | Medium — EMA/RSI/MACD overlap | Medium | Code (mixed w/ tests) |
| [freqtrade/freqtrade-strategies](https://github.com/freqtrade/freqtrade-strategies) | 66 | Freqtrade `IStrategy` | **Active** | **18 ported** — see `freqtrade_ported/catalog.py` | Easy–medium | Code |
| [Freqtrade Strategies Hub](https://fts.naif.one/) | ~12,905 | Aggregated metadata | Active indexer | Unknown per-strategy | N/A | **Meta catalog** |

---

## Tier 2 — Medium Collections (10–50)

| Repo | ~Count | Format | Maintenance | Overlap w/ ported | Portability | Code vs catalog |
|------|-------:|--------|-------------|-------------------|-------------|-----------------|
| [je-suis-tm/quant-trading](https://github.com/je-suis-tm/quant-trading) | 15 TA + 3 quantamental | Pandas backtest scripts | **Active** (2026) | **5 ported**, 3 dedup-skipped | Medium | Code |
| [ulandz/ai-trader](https://github.com/ulandz/ai-trader) | 25 | Backtrader `BaseStrategy` + YAML | Active | Medium | Medium | Code |
| [leosmigel/analyzingalpha](https://github.com/leosmigel/analyzingalpha) | ~36 | Python (book companion) | Moderate | Low | Medium | Code |
| [chrism2671/PyTrendFollow](https://github.com/chrism2671/PyTrendFollow) | ~35 | Futures trend-following framework | Moderate | Low | Hard (multi-contract) | Code |
| [jesse-ai/example-strategies](https://github.com/jesse-ai/example-strategies) | 12 | Jesse `Strategy` folders | Stale (2024-03) | Low–medium | Medium | Code |
| [marketcalls/vectorbt-backtesting-skills](https://github.com/marketcalls/vectorbt-backtesting-skills) | 12 templates | vectorbt signal scripts | Active (2026) | Medium — EMA/RSI/MACD/Donchian | Medium | Code |
| [ali-azary/Algorithmic-Trading-From-Beginner-to-Advanced](https://github.com/ali-azary/Algorithmic-Trading-From-Beginner-to-Advanced) | 11 | Backtrader `bt.Strategy` | Active (2026) | Low | Medium | Code |
| [kevinwudev/madtrader](https://github.com/kevinwudev/madtrader) | 9 | vectorbt + notebooks | Moderate | Medium | Medium | Code |
| [hummingbot/hummingbot](https://github.com/hummingbot/hummingbot) | 9 V1 + V2 controllers + 17 scripts | Cython/Python MM & arb | **Active** | Low — MM/arb not TA ports | Hard (microstructure) | Code |
| [FinRL](https://github.com/AI4Finance-Foundation/FinRL) notebooks | 10 | DRL notebooks | Maintenance mode → FinRL-X | Low | Hard (DRL) | Code |
| [aldrinmagno/FreqtradeStrategies](https://github.com/aldrinmagno/FreqtradeStrategies) | 5 | Freqtrade (Bybit scalping) | Active | **High** — BbandRsi, Cluc variants | Easy–medium | Code |
| [paulcpk/freqtrade-strategies-that-work](https://github.com/paulcpk/freqtrade-strategies-that-work) | 5 | Freqtrade | Stale (2021) | High | Easy | Code |
| [olonok69/QUANT](https://github.com/olonok69/QUANT) | ~15 | Zipline + Backtrader notebooks | Moderate | Medium | Medium–hard | Code |
| [purvasingh96/AI-for-Trading](https://github.com/purvasingh96/AI-for-Trading) | 8 projects | Zipline / Alphalens | Stale | Low | Hard | Code |
| [ysdede/jesse_strategies](https://github.com/ysdede/jesse_strategies) | ~10+ | Jesse | Moderate | Medium | Medium | Code |
| [gabrielweich/jesse-strategies](https://github.com/gabrielweich/jesse-strategies) | ~10 | Jesse | Moderate | Medium | Medium | Code |
| [bustillo/freqtrade-strategies](https://github.com/bustillo/freqtrade-strategies) | ~3–5 | Freqtrade futures DCA | Active (2025) | Low (futures) | Hard (short/DCA) | Code |
| [i1ya/freqtrade-strategies](https://github.com/i1ya/freqtrade-strategies) | 8 | Freqtrade | Stale (2021) | High | Easy | Code |
| [Drakkar-Software/OctoBot-Tentacles](https://github.com/Drakkar-Software/OctoBot-Tentacles) | ~20+ evaluators | OctoBot tentacle modules | Active | Low | Hard | Code |
| [AI4Finance-Foundation/FinRL-Trading](https://github.com/AI4Finance-Foundation/FinRL-Trading) (FinRL-X) | 3 use cases | Weight-centric ML/DRL | **Active** | Low | Hard | Code |

---

## Tier 3 — Awesome Lists / Link Catalogs

| Repo | ~Strategy refs | Format | Maintenance | Notes |
|------|---------------:|--------|-------------|-------|
| [wangzhe3224/awesome-systematic-trading](https://github.com/wangzhe3224/awesome-systematic-trading) | 40+ linked | Markdown awesome list | **Active** (2026) | **Already used**; links to quant-trading, fmz, czsc, etc. |
| [paperswithbacktest/awesome-systematic-trading](https://github.com/paperswithbacktest/awesome-systematic-trading) | 40+ papers + **180 code** | List + `static/strategies/` | Moderate | Fork/continuation of systematic-trading list; **also Tier 1 code** |
| [wilsonfreitas/awesome-quant](https://github.com/wilsonfreitas/awesome-quant) | 200+ lib links | Awesome list | **Active** (2026) | Libraries, not strategy code — discovery only |
| [just-nilux/awesome-freqtrade](https://github.com/just-nilux/awesome-freqtrade) | ~30 snippets | Freqtrade snippets + links | Active | Discord-sourced; not a strategy pack |
| [jesse-ai/awesome-jesse](https://github.com/jesse-ai/awesome-jesse) | ~20 links | Jesse community list | Active (2025) | Points to example-strategies + community repos |
| [grananqvist/Awesome-Quant-Machine-Learning-Trading](https://github.com/grananqvist/Awesome-Quant-Machine-Learning-Trading) | 100+ links | ML trading resources | Active | Papers/repos; not vendored code |
| [leoncuhk/awesome-quant-ai](https://github.com/leoncuhk/awesome-quant-ai) | 50+ links | AI/ML quant list | Active | Discovery |
| [thuquant/awesome-quant](https://github.com/thuquant/awesome-quant) | 100+ links | Chinese quant index | Active | Discovery (CN) |
| [AI4Finance-Foundation/Awesome_AI4Finance](https://github.com/AI4Finance-Foundation/Awesome_AI4Finance) | 50+ links | AI finance list | Active | Links QuantsPlaybook, FinRL, etc. |
| [0voice/Awesome-QuantDev-Learn](https://github.com/0voice/Awesome-QuantDev-Learn) | 80+ links | Chinese learning path | Active | Tutorials, not strategies |
| [SiriusChu/awesome-systematic-trading-V2](https://github.com/SiriusChu/awesome-systematic-trading-V2) | 40+ | Fork of paperswithbacktest list | Stale | Duplicate of Tier 3 entry above |
| [Quanturf/AlgoTrading](https://github.com/Quanturf/AlgoTrading) | 61 papers | Academic list + some QC scripts | Moderate | Overlaps paperswithbacktest |

---

## Tier 4 — Frameworks & Single-Strategy Repos

| Repo | Role | Strategy count | Portability | Notes |
|------|------|---------------:|-------------|-------|
| [freqtrade/freqtrade](https://github.com/freqtrade/freqtrade) | Bot framework | 1 sample | N/A | `SampleStrategy` only — use freqtrade-strategies repo |
| [jesse-ai/jesse](https://github.com/jesse-ai/jesse) | Bot framework | Built-in examples | Medium | Framework itself; strategies in example-strategies |
| [hummingbot/hummingbot](https://github.com/hummingbot/hummingbot) | MM/arb bot | ~9 V1 templates | Hard | Not directional TA; market-making focus |
| [mementum/backtrader](https://github.com/mementum/backtrader) | Backtest framework | ~5 samples | Medium | Samples in `samples/` — use ali-azary pack instead |
| [cloudQuant/backtrader](https://github.com/cloudQuant/backtrader) | backtrader fork | 1271 test strategies | Medium | Regression tests, not a curated port list |
| [polakowo/vectorbt](https://github.com/polakowo/vectorbt) | Vectorized backtester | Examples only | Medium | Signal-based; no event-driven `Strategy` class |
| [pmorissette/bt](https://github.com/pmorissette/bt) | Algo stacks | ~0 standalone | Hard | Composable algos, not discrete strategies |
| [stefan-jansen/zipline-reloaded](https://github.com/stefan-jansen/zipline-reloaded) | Zipline fork | ~10 examples | Hard | Pipeline/universe model |
| [Limex-com/ziplime](https://github.com/Limex-com/ziplime) | Zipline rewrite | AI-generated | Hard | Modern fork; few fixed templates |
| [iterativv/NostalgiaForInfinity](https://github.com/iterativv/NostalgiaForInfinity) | Mega Freqtrade strategy | **1** (multi-signal) | Hard | 3.3k★; hyper-complex, multi-TF — also mirrored in davidzr |
| [virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) | LLM agent stack | ~12 agents | Hard | Agent portfolio decisions, not bar TA |
| [td-02/ai-native-hedge-fund](https://github.com/td-02/ai-native-hedge-fund) | Agent + Alpaca | ~5 strategy agents | Hard | Multi-agent weights |
| [Drakkar-Software/OctoBot](https://github.com/Drakkar-Software/OctoBot) | Crypto bot | Built-in modes | Hard | Grid/DCA/TV — not TA library |
| [waditu/czsc](https://github.com/waditu/czsc) | Chan theory analytics | Signal functions | Hard | Chinese technical analysis framework |
| [darkvolg/trendrider-strategy](https://github.com/darkvolg/trendrider-strategy) | Freqtrade strategy | 1 | Medium | Listed in awesome-systematic-trading crypto_focus |
| [financial-astrology-research/jesse-astrology-trading-strategy](https://github.com/financial-astrology-research/jesse-astrology-trading-strategy) | Jesse niche | 1 | Hard | Astrology/ML hybrid |

---

## Ecosystem Notes

### Freqtrade ecosystem

- **Canonical source:** `freqtrade/freqtrade-strategies` (66 strategies, actively maintained).
- **Community forks** (`davidzr`, `werkkrew`, `keithorange`, `i1ya`, `paulcpk`) are largely overlapping scrapes or personal forks — run `freqtrade_ported/scripts/analyze_source.py` before porting.
- **NostalgiaForInfinity** is the most famous single community strategy (not in official repo); treat as one hard port, not a collection.
- **awesome-freqtrade** and **Freqtrade Strategies Hub** are for discovery.

### Jesse ecosystem

- **jesse-ai/example-strategies** (12) is the official sample pack.
- **jesse-ai/awesome-jesse** links community repos (`ysdede/jesse_strategies`, etc.).
- Built-in `jesse/strategies/` is mostly regression tests — not primary port targets.

### Backtrader / bt / vectorbt

- **ali-azary** pack is the best small curated Backtrader set for learning ports.
- **vectorbt** repos express logic as boolean signal arrays — port by extracting entry/exit conditions into `on_bar`.
- **pmorissette/bt** is portfolio algo composition, not a strategy library.

### QuantConnect / Lean

- **427** Python algorithms in `Algorithm.Python/` — regression examples for Lean features (universe, options, futures).
- **paperswithbacktest** vendored scripts are the most port-friendly academic subset (still hard vs crypto bar strategies).

### Exchange-specific / Chinese quant

- **fmzquant/strategies** — largest link catalog; strategies run on FMZ cloud, not standalone Python.
- **hugo2046/QuantsPlaybook** — A-share factor research; high count but notebook-centric.
- **aldrinmagno/FreqtradeStrategies** — Bybit-focused scalping bundle.

### Open-source “hedge fund” repos

- **ai-hedge-fund**, **ai-native-hedge-fund**, **FinRL-X** — agent/weight pipelines, not discrete TA strategies. Low priority for `freqtrade_ported`-style ports.

---

## Dedup Notes vs Existing Ports

### freqtrade_ported (22 strategies from official repo)

| Already ported | Do not re-port from |
|----------------|---------------------|
| BbandRsi, Simple, MACD*, AverageStrategy, UniversalMACD, Low_BB, DoesNothing, Strategy001, Diamond, hlhb, AdxSmas, AwesomeMacd, CMCWinner, TechnicalExample, Scalp, Bandtastic, ADXMomentum, **HourBased**, **SwingHighToSky**, **MultiMa**, **PowerTower** | davidzr, werkkrew, keithorange, paulcpk, i1ya copies of same class names |

**Safe to port next from official repo** (single-TF, long-only candidates): `Quickie` (TEMA now available), `SmoothScalp`, `ClucMay72018`, `Supertrend` (SuperTrend indicator added).

**Blocked in official repo** (need framework work first): multi-TF (`MultiRSI`, `InformativeSample`), futures/, custom_stoploss, TALib CDL patterns, lookahead demos.

### systematic_trading_ported (5 from quant-trading)

| Ported | Dedup — use existing module |
|--------|------------------------------|
| DualThrust, LondonBreakout, ParabolicSar, HeikinAshiMarubozu, BollingerBottomW | MACD Oscillator → `AverageStrategy`; Awesome Oscillator → `AwesomeMacd`; RSI Pattern → `BbandRsi` |

**quant-trading remaining:** Shooting Star (short), Pair Trading (2-leg), Options Straddle, VIX Calculator, Monte Carlo/Oil/Smart Farmers projects — blocked or out of scope.

### Cross-source duplicates (do not double-port)

| Logic | Sources |
|-------|---------|
| BB + RSI mean reversion | freqtrade `BbandRsi`, quant-trading RSI, aldrinmagno, NFI signals |
| ADX + SMA | freqtrade `AdxSmas`, davidzr `ADXMomentum` variants |
| Heikin Ashi | freqtrade `Strategy001` vs quant-trading marubozu (different rules — both kept) |
| Dual Thrust / London breakout | quant-trading (ported), Jesse `DUAL_THRUST`, fmz links |
| EMA cross | freqtrade `AverageStrategy`, Jesse `SMACrossover`, vectorbt templates, nautilus `ema_cross*` |

---

## Recommended Porting Priority

Priority balances **unique logic**, **portability**, and **dedup** against work already in `freqtrade_ported/` and `systematic_trading_ported/`.

| Priority | Repo | Rationale |
|----------|------|-----------|
| **1** | `freqtrade/freqtrade-strategies` (remaining ~43) | Existing base class, catalog, and analyze script |
| **2** | `paperswithbacktest/awesome-systematic-trading` `static/strategies/` | Bar-based simplifications where possible; most QC universe scripts blocked |
| **3** | `jesse-ai/example-strategies` | **7/12 ported** — MAGen, KDJ remain |
| **4** | `ali-azary/Algorithmic-Trading-From-Beginner-to-Advanced` | 11 Backtrader strategies with clear signal logic |
| **5** | `je-suis-tm/quant-trading` (exhausted for TA) | Only blocked items remain — skip unless extending to pairs/options |
| **6** | `marketcalls/vectorbt-backtesting-skills` | 12 templates — extract signals into Nautilus |
| **7** | `Astralchemist/Quant-Algos` | Curate ~20–30 non-overlapping from 311 files |
| **8** | `kevinwudev/madtrader` | 9 vectorbt TA strategies + notebooks |
| **9** | `davidzr/freqtrade-strategies` | After dedup scan — only net-new class names |
| **10** | `keithorange/HUGE_FreqTrade_Strategy_Collection` | Last — bulk scrape; use hub/dedup tooling |

**Defer / separate track:** `QuantConnect/Lean` (427), `fmzquant/strategies` (FMZ runtime), `hugo2046/QuantsPlaybook` (A-share notebooks), hummingbot MM, FinRL/DRL, agent hedge-fund repos.

---

## Top 10 Repos to Port Next

| # | Repository | ~New strategies | Why |
|---|------------|----------------:|-----|
| 1 | [freqtrade/freqtrade-strategies](https://github.com/freqtrade/freqtrade-strategies) | ~43 remaining | Infrastructure done; finish catalog |
| 2 | [paperswithbacktest/awesome-systematic-trading](https://github.com/paperswithbacktest/awesome-systematic-trading) | ~58 bar-simplifiable | Most are QC universe — catalog in `academic_ported/` |
| 3 | [jesse-ai/example-strategies](https://github.com/jesse-ai/example-strategies) | 5 remaining | MAGen, KDJ blocked |
| 4 | [ali-azary/Algorithmic-Trading-From-Beginner-to-Advanced](https://github.com/ali-azary/Algorithmic-Trading-From-Beginner-to-Advanced) | 8 remaining | Quantile/regime/ML strategies blocked |
| 5 | [marketcalls/vectorbt-backtesting-skills](https://github.com/marketcalls/vectorbt-backtesting-skills) | 8 remaining | sda2, dual_momentum rotation, DCA templates |
| 6 | [Astralchemist/Quant-Algos](https://github.com/Astralchemist/Quant-Algos) | ~50 curated | Broad categories after dedup pass |
| 7 | [ulandz/ai-trader](https://github.com/ulandz/ai-trader) | ~20 | Config-driven Backtrader classics |
| 8 | [kevinwudev/madtrader](https://github.com/kevinwudev/madtrader) | 9 | vectorbt TA with clear signals |
| 9 | [leosmigel/analyzingalpha](https://github.com/leosmigel/analyzingalpha) | ~15 tradeable | Book-quality Python strategies |
| 10 | [davidzr/freqtrade-strategies](https://github.com/davidzr/freqtrade-strategies) | ~50–100 net-new | After automated dedup vs official + HUGE collection |

---

## Full Catalog Table (all sources)

| Tier | Repo | URL | ~Count | Framework | Active? | Overlap | Port | Type |
|------|------|-----|-------:|-----------|---------|---------|------|------|
| 1 | HUGE_FreqTrade_Strategy_Collection | https://github.com/keithorange/HUGE_FreqTrade_Strategy_Collection | 478 | Freqtrade | Stale | High | Easy–Med | Code |
| 1 | davidzr/freqtrade-strategies | https://github.com/davidzr/freqtrade-strategies | 465 | Freqtrade | Low | High | Easy–Med | Code |
| 1 | QuantConnect/Lean | https://github.com/QuantConnect/Lean | 427 | QCAlgorithm | **Yes** | Low | Hard | Code |
| 1 | Astralchemist/Quant-Algos | https://github.com/Astralchemist/Quant-Algos | 311 | Python | **Yes** | Low | Med | Code |
| 1 | paperswithbacktest/awesome-systematic-trading | https://github.com/paperswithbacktest/awesome-systematic-trading | 180 | QCAlgorithm | Mod | Low | Hard | Hybrid |
| 1 | hugo2046/QuantsPlaybook | https://github.com/hugo2046/QuantsPlaybook | 100+ | Notebooks | **Yes** | Low | Hard | Code |
| 1 | fmzquant/strategies | https://github.com/fmzquant/strategies | ~5800 | Multi | Mod | Med | Hard | Catalog |
| 1 | werkkrew/freqtrade-strategies | https://github.com/werkkrew/freqtrade-strategies | 122 | Freqtrade | Stale | High | Easy–Med | Code |
| 1 | jesse-ai/jesse strategies | https://github.com/jesse-ai/jesse | 145 | Jesse | **Yes** | Med | Med | Code |
| 1 | freqtrade/freqtrade-strategies | https://github.com/freqtrade/freqtrade-strategies | 66 | Freqtrade | **Yes** | 22 ported | Easy–Med | Code |
| 1 | Freqtrade Strategies Hub | https://fts.naif.one/ | 12905 | Mixed | **Yes** | Unknown | N/A | Meta |
| 2 | je-suis-tm/quant-trading | https://github.com/je-suis-tm/quant-trading | 15 | Pandas | **Yes** | 5 ported | Med | Code |
| 2 | ulandz/ai-trader | https://github.com/ulandz/ai-trader | 25 | Backtrader | **Yes** | Med | Med | Code |
| 2 | leosmigel/analyzingalpha | https://github.com/leosmigel/analyzingalpha | 36 | Python | Mod | Low | Med | Code |
| 2 | chrism2671/PyTrendFollow | https://github.com/chrism2671/PyTrendFollow | 35 | Python futures | Mod | Low | Hard | Code |
| 2 | jesse-ai/example-strategies | https://github.com/jesse-ai/example-strategies | 12 | Jesse | Stale | Low | Med | Code |
| 2 | vectorbt-backtesting-skills | https://github.com/marketcalls/vectorbt-backtesting-skills | 12 | vectorbt | **Yes** | Med | Med | Code |
| 2 | ali-azary/Algorithmic-Trading | https://github.com/ali-azary/Algorithmic-Trading-From-Beginner-to-Advanced | 11 | Backtrader | **Yes** | Low | Med | Code |
| 2 | kevinwudev/madtrader | https://github.com/kevinwudev/madtrader | 9 | vectorbt | Mod | Med | Med | Code |
| 2 | hummingbot/hummingbot | https://github.com/hummingbot/hummingbot | ~26 | Hummingbot | **Yes** | Low | Hard | Code |
| 2 | FinRL notebooks | https://github.com/AI4Finance-Foundation/FinRL | 10 | DRL | Maint | Low | Hard | Code |
| 2 | aldrinmagno/FreqtradeStrategies | https://github.com/aldrinmagno/FreqtradeStrategies | 5 | Freqtrade | **Yes** | High | Easy–Med | Code |
| 2 | paulcpk/freqtrade-strategies-that-work | https://github.com/paulcpk/freqtrade-strategies-that-work | 5 | Freqtrade | Stale | High | Easy | Code |
| 2 | olonok69/QUANT | https://github.com/olonok69/QUANT | 15 | Zipline/BT | Mod | Med | Med–Hard | Code |
| 2 | purvasingh96/AI-for-Trading | https://github.com/purvasingh96/AI-for-Trading | 8 | Zipline | Stale | Low | Hard | Code |
| 2 | ysdede/jesse_strategies | https://github.com/ysdede/jesse_strategies | 10+ | Jesse | Mod | Med | Med | Code |
| 2 | gabrielweich/jesse-strategies | https://github.com/gabrielweich/jesse-strategies | 10 | Jesse | Mod | Med | Med | Code |
| 2 | bustillo/freqtrade-strategies | https://github.com/bustillo/freqtrade-strategies | 5 | Freqtrade | **Yes** | Low | Hard | Code |
| 2 | i1ya/freqtrade-strategies | https://github.com/i1ya/freqtrade-strategies | 8 | Freqtrade | Stale | High | Easy | Code |
| 2 | OctoBot-Tentacles | https://github.com/Drakkar-Software/OctoBot-Tentacles | 20+ | OctoBot | **Yes** | Low | Hard | Code |
| 2 | FinRL-Trading (FinRL-X) | https://github.com/AI4Finance-Foundation/FinRL-Trading | 3 | ML/DRL | **Yes** | Low | Hard | Code |
| 3 | wangzhe3224/awesome-systematic-trading | https://github.com/wangzhe3224/awesome-systematic-trading | 40+ links | List | **Yes** | 5 ported | N/A | Catalog |
| 3 | wilsonfreitas/awesome-quant | https://github.com/wilsonfreitas/awesome-quant | 200+ links | List | **Yes** | — | N/A | Catalog |
| 3 | just-nilux/awesome-freqtrade | https://github.com/just-nilux/awesome-freqtrade | 30 | List/snippets | **Yes** | — | N/A | Catalog |
| 3 | jesse-ai/awesome-jesse | https://github.com/jesse-ai/awesome-jesse | 20 | List | Active | — | N/A | Catalog |
| 3 | grananqvist/Awesome-Quant-ML-Trading | https://github.com/grananqvist/Awesome-Quant-Machine-Learning-Trading | 100+ | List | **Yes** | — | N/A | Catalog |
| 3 | leoncuhk/awesome-quant-ai | https://github.com/leoncuhk/awesome-quant-ai | 50+ | List | **Yes** | — | N/A | Catalog |
| 3 | thuquant/awesome-quant | https://github.com/thuquant/awesome-quant | 100+ | List | **Yes** | — | N/A | Catalog |
| 3 | Awesome_AI4Finance | https://github.com/AI4Finance-Foundation/Awesome_AI4Finance | 50+ | List | **Yes** | — | N/A | Catalog |
| 3 | Awesome-QuantDev-Learn | https://github.com/0voice/Awesome-QuantDev-Learn | 80+ | List | **Yes** | — | N/A | Catalog |
| 3 | SiriusChu/awesome-systematic-trading-V2 | https://github.com/SiriusChu/awesome-systematic-trading-V2 | 40+ | List | Stale | — | N/A | Catalog |
| 3 | Quanturf/AlgoTrading | https://github.com/Quanturf/AlgoTrading | 61 | List + some code | Mod | Med | Hard | Hybrid |
| 4 | freqtrade/freqtrade | https://github.com/freqtrade/freqtrade | 1 sample | Framework | **Yes** | — | N/A | Framework |
| 4 | jesse-ai/jesse | https://github.com/jesse-ai/jesse | Framework | Framework | **Yes** | — | Med | Framework |
| 4 | hummingbot/hummingbot | https://github.com/hummingbot/hummingbot | Framework | Framework | **Yes** | — | Hard | Framework |
| 4 | mementum/backtrader | https://github.com/mementum/backtrader | ~5 samples | Framework | Maint | — | Med | Framework |
| 4 | cloudQuant/backtrader | https://github.com/cloudQuant/backtrader | 1271 tests | Framework | **Yes** | — | Med | Framework |
| 4 | polakowo/vectorbt | https://github.com/polakowo/vectorbt | Examples | Framework | Maint | — | Med | Framework |
| 4 | pmorissette/bt | https://github.com/pmorissette/bt | Algos | Framework | Maint | — | Hard | Framework |
| 4 | zipline-reloaded | https://github.com/stefan-jansen/zipline-reloaded | 10 | Framework | Maint | — | Hard | Framework |
| 4 | ziplime | https://github.com/Limex-com/ziplime | AI-gen | Framework | **Yes** | — | Hard | Framework |
| 4 | NostalgiaForInfinity | https://github.com/iterativv/NostalgiaForInfinity | 1 mega | Freqtrade | **Yes** | Med | Hard | Code |
| 4 | virattt/ai-hedge-fund | https://github.com/virattt/ai-hedge-fund | Agents | LLM agents | **Yes** | — | Hard | Code |
| 4 | td-02/ai-native-hedge-fund | https://github.com/td-02/ai-native-hedge-fund | Agents | LLM agents | **Yes** | — | Hard | Code |
| 4 | Drakkar-Software/OctoBot | https://github.com/Drakkar-Software/OctoBot | Modes | Bot | **Yes** | — | Hard | Framework |
| 4 | waditu/czsc | https://github.com/waditu/czsc | Chan TA | Library | **Yes** | — | Hard | Code |
| 4 | darkvolg/trendrider-strategy | https://github.com/darkvolg/trendrider-strategy | 1 | Freqtrade | Mod | — | Med | Code |

**Total catalogued: 52** entries (11 Tier 1 · 18 Tier 2 · 11 Tier 3 · 12 Tier 4).

---

## Methodology

- GitHub search via `gh search repos` (unauthenticated; July 2026).
- File counts via GitHub Trees/Contents API (`git/trees?recursive=1`, paginated `contents/`).
- Local clone verification: `.freqtrade-strategies-source/` → **66** `.py` strategy files.
- Web search for ecosystem hubs (Freqtrade Hub, NFI, awesome lists).
- Stars/push dates from GitHub API as maintenance proxy.

## Related files in this repo

- `freqtrade_ported/catalog.py` — per-strategy port status for official Freqtrade repo
- `freqtrade_ported/scripts/analyze_source.py` — scan cloned Freqtrade trees for dedup
- `systematic_trading_ported/catalog.py` — awesome-list → quant-trading entries
- `systematic_trading_ported/dedup.py` — cross-package dedup mapping
- `jesse_ported/catalog.py` — jesse-ai/example-strategies port status
- `vectorbt_ported/catalog.py` — vectorbt template port status
- `backtrader_ported/catalog.py` — ali-azary Backtrader pack status
- `quant_algos_ported/catalog.py` — Astralchemist/Quant-Algos scaffold dedup (no runnable ports)

- `academic_ported/catalog.py` — paperswithbacktest QC scripts (mostly blocked)

**Source clones (hidden dirs):** `.freqtrade-strategies-source/`, `.jesse-source/`, `.backtrader-ali-source/`, `.papers-source/`, `.vectorbt-skills-source/`, `.quant-trading-source/`, `.quant-algos-source/`, `.analyzingalpha-source/`
