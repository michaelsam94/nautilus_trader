# Freqtrade Strategy Ports

Ports of community strategies from [freqtrade/freqtrade-strategies](https://github.com/freqtrade/freqtrade-strategies) to Nautilus Trader.

**These are example strategies with no alpha advantage. Not intended for live trading.**

## Summary

| Metric | Count |
|--------|------:|
| Total upstream strategies | 65 |
| Ported (full) | 19 |
| Ported (partial) | 3 |
| Blocked / not ported | 39 |
| Deprecated (lookahead examples) | 4 |

## Directory structure

```
nautilus_trader/examples/strategies/freqtrade_ported/
├── README.md                 # This file
├── __init__.py               # Public exports
├── base.py                   # FreqtradeLongOnlyStrategy base class
├── helpers.py                # Cross detection, RSI scale, rolling mean
├── indicators.py             # TALib-gap indicators (MACD signal, ADX, Heikin Ashi, …)
├── catalog.py                # Full upstream catalog with port status
├── scripts/
│   └── analyze_source.py     # Scan cloned Freqtrade repo vs catalog
├── bband_rsi.py              # Individual ported strategies
├── simple_strategy.py
├── macd_strategy.py
└── …
```

Clone the upstream repo locally (already at `.freqtrade-strategies-source/` in workspace root):

```bash
git clone --depth 1 https://github.com/freqtrade/freqtrade-strategies.git .freqtrade-strategies-source
```

## Freqtrade → Nautilus mapping

| Freqtrade | Nautilus Trader |
|-----------|-----------------|
| `IStrategy` | `FreqtradeLongOnlyStrategy` → `Strategy` |
| `populate_indicators()` | Indicators in `__init__` + `register_indicator_for_bars()` |
| `populate_entry_trend()` | `check_entry(bar) -> bool` |
| `populate_exit_trend()` | `check_exit(bar) -> bool` |
| `timeframe` | `BarType` in config (e.g. `BTCUSDT.BINANCE-5-MINUTE-LAST-INTERNAL`) |
| `minimal_roi` / `stoploss` / `trailing_stop` | **Not auto-mapped** — use Nautilus risk/trailing stop components |
| `custom_stoploss()` / `custom_exit()` | Implement in `on_bar` or order event handlers |
| `informative_pairs()` / `merge_informative_pair` | Subscribe to additional `BarType`s or use actors |
| `qtpylib.crossed_above(a, b)` | `CrossDetector.crossed_above(a, b)` in `helpers.py` |
| `dataframe['x'].shift(1)` | `ShiftedValue.update(x)` |
| `ta.RSI` (0–100) | `RelativeStrengthIndex` (0–1) — use `rsi_from_freqtrade()` |
| `ta.MACD` + signal | `MacdWithSignal` in `indicators.py` |
| `ta.ADX` / `PLUS_DI` / `MINUS_DI` | `AverageDirectionalIndex` |
| `qtpylib.heikinashi` | `HeikinAshi` |
| `ta.MFI` / `ta.CMO` | `MoneyFlowIndex` / `ChandeMomentumOscillator` |
| `enter_long` / `exit_long` | `enter_long()` / `exit_long()` market orders |
| Hyperopt `IntParameter` etc. | Frozen config fields with upstream defaults |

## Ported strategies

| Freqtrade name | Nautilus class | Notes |
|----------------|----------------|-------|
| BbandRsi | `BbandRsi` | |
| Simple | `Simple` | |
| MACDStrategy | `MacdStrategy` | |
| MACDStrategy_crossed | `MacdStrategyCrossed` | |
| AverageStrategy | `AverageStrategy` | |
| UniversalMACD | `UniversalMacd` | |
| Low_BB | `LowBb` | Partial — exit via ROI/trailing in FT only |
| DoesNothingStrategy | `DoesNothing` | Skeleton |
| Strategy001 | `Strategy001` | Heikin Ashi + EMA |
| Diamond | `Diamond` | Pure OHLCV crossover |
| hlhb | `Hlhb` | |
| AdxSmas | `AdxSmas` | |
| AwesomeMacd | `AwesomeMacd` | |
| CMCWinner | `CmcWinner` | Uses prior-bar values |
| TechnicalExampleStrategy | `TechnicalExample` | CMF |
| Scalp | `Scalp` | |
| Bandtastic | `Bandtastic` | Partial — simplified BB bands |
| ADXMomentum | `AdxMomentum` | Partial — SAR omitted |

## Usage example

```python
from decimal import Decimal

from nautilus_trader.examples.strategies.freqtrade_ported import BbandRsi
from nautilus_trader.examples.strategies.freqtrade_ported import BbandRsiConfig
from nautilus_trader.model.data import BarType
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.test_kit.providers import TestInstrumentProvider

instrument = TestInstrumentProvider.btcusdt_binance()
config = BbandRsiConfig(
    instrument_id=instrument.id,
    bar_type=BarType.from_str(f"{instrument.id}-5-MINUTE-LAST-INTERNAL"),
    trade_size=Decimal("0.01"),
)
strategy = BbandRsi(config)
```

Wire into a `BacktestNode` or `TradingNode` like any other `Strategy`.

## Not ported (and why)

See `catalog.py` for the full list. Common blockers:

- **Multi-timeframe** — `MultiRSI`, `ReinforcedAverageStrategy`, `CCIStrategy`, `multi_tf`
- **Futures / short** — everything under `futures/`
- **Custom callbacks** — `CustomStoplossWithPSAR`, `FixedRiskRewardLoss`, `BreakEven`
- **TALib candlestick patterns** — `Strategy002`, `PatternRecognition`
- **Lookahead bias demos** — `lookahead_bias/*` (deprecated)
- **Heavy hyperopt / genetic** — `GodStra`, `Supertrend`, `BinHV*`
- **Niche indicators** — `TDSequential`, `PowerTower`, `TEMA` (Quickie)

## Automating remaining ports

1. Run `python -m nautilus_trader.examples.strategies.freqtrade_ported.scripts.analyze_source`
2. Pick a `blocked` entry from `catalog.py`
3. Subclass `FreqtradeLongOnlyStrategy`, map indicators via `indicators.py` or built-ins
4. Add tests under `tests/` mirroring `python/tests/strategies/`
5. Update `catalog.py` status

Template for new ports:

```python
class MyStrategyConfig(FreqtradePortConfig, frozen=True):
    ...

class MyStrategy(FreqtradeLongOnlyStrategy):
    def _register_indicators(self) -> None: ...
    def check_entry(self, bar: Bar) -> bool: ...
    def check_exit(self, bar: Bar) -> bool: ...
```

## Related: systematic_trading_ported

Strategies from [awesome-systematic-trading](https://github.com/wangzhe3224/awesome-systematic-trading) live in `nautilus_trader/examples/strategies/systematic_trading_ported/`. That repo is an awesome **list** (not strategy code); ports come from linked repos (mainly `je-suis-tm/quant-trading`). See `systematic_trading_ported/dedup.py` for overlap with this package.

## Limitations

- Long-only spot logic; short/futures entries not mapped
- Freqtrade ROI tables and trailing stops are not replicated
- Volume filters assume bar volume is populated on `Bar` objects
- Indicator values may differ slightly from TALib due to implementation details
- Hyperopt parameter ranges are collapsed to single default values

## VPS deployment (next steps)

1. Copy or `git pull` this repo on the VPS (`root@80.208.228.117`)
2. Install/build Nautilus Trader per project docs
3. Register chosen strategy in your `TradingNode` config
4. Map exchange instrument IDs and `BarType` to your data subscriptions
5. Backtest locally before live deployment
