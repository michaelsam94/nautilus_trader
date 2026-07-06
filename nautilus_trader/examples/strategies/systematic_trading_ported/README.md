# Systematic Trading Strategy Ports

Ports strategies referenced by [awesome-systematic-trading](https://github.com/wangzhe3224/awesome-systematic-trading) into Nautilus Trader.

**Important:** `awesome-systematic-trading` is a curated **awesome list** of libraries and resources — it does **not** contain strategy source code. Executable strategies live in **linked repositories** (primarily [je-suis-tm/quant-trading](https://github.com/je-suis-tm/quant-trading)).

This package reuses infrastructure from `freqtrade_ported/` (`FreqtradeLongOnlyStrategy`, `helpers.py`, shared indicators) and avoids duplicating strategies already ported there.

## Summary

| Metric | Count |
|--------|------:|
| Catalogued alpha entries | 20 |
| **Newly ported** | 5 |
| **Skipped (dedup)** | 3 |
| **Blocked** | 7 |
| **External (not vendored)** | 5 |

## Directory structure

```
nautilus_trader/examples/strategies/systematic_trading_ported/
├── README.md
├── __init__.py
├── catalog.py          # Port status for awesome-list alpha entries
├── dedup.py            # Explicit dedup mapping vs freqtrade_ported
├── indicators.py       # ParabolicSar, DualThrustRange
├── dual_thrust.py
├── london_breakout.py
├── parabolic_sar.py
├── heikin_ashi_marubozu.py
└── bollinger_bottom_w.py
```

Source clones (workspace root):

- `.awesome-systematic-trading-source/` — the awesome list
- `.quant-trading-source/` — primary alpha strategy implementations

## Ported strategies

| Source | Nautilus class | Notes |
|--------|----------------|-------|
| quant-trading Dual Thrust | `DualThrust` | Session breakout; needs intraday bars + UTC session hours |
| quant-trading London Breakout | `LondonBreakout` | Tokyo range → London open long |
| quant-trading Parabolic SAR | `ParabolicSarStrategy` | Close vs SAR crossover |
| quant-trading Heikin-Ashi | `HeikinAshiMarubozu` | Marubozu rules (≠ Strategy001 EMA combo) |
| quant-trading Bollinger W | `BollingerBottomW` | Simplified bottom-W vs full five-node scan |

## Dedup — skipped (use freqtrade_ported instead)

| quant-trading strategy | Duplicate of |
|------------------------|--------------|
| MACD Oscillator | `AverageStrategy` / `MacdStrategy` (MA crossover family) |
| Awesome Oscillator | `AwesomeMacd` |
| RSI Pattern Recognition | `BbandRsi` (RSI 30/70 mean reversion) |

## Blocked

| Strategy | Reason |
|----------|--------|
| Shooting Star | Short-only candlestick pattern |
| Pair Trading | Two-instrument cointegration |
| Options Straddle | Options multi-leg |
| VIX Calculator | Vol index tool, not a signal strategy |
| Monte Carlo / Oil Money / Smart Farmers | Quantamental projects, not bar TA |

## External (awesome list links only)

`analyzingalpha`, `PyTrendFollow`, `czsc`, `fmzquant/strategies`, `TrendRider` — require separate clone/port efforts.

## Usage

```python
from decimal import Decimal

from nautilus_trader.examples.strategies.systematic_trading_ported import DualThrust
from nautilus_trader.examples.strategies.systematic_trading_ported import DualThrustConfig
from nautilus_trader.model.data import BarType
from nautilus_trader.test_kit.providers import TestInstrumentProvider

instrument = TestInstrumentProvider.btcusdt_binance()
config = DualThrustConfig(
    instrument_id=instrument.id,
    bar_type=BarType.from_str(f"{instrument.id}-1-MINUTE-LAST-INTERNAL"),
    trade_size=Decimal("0.01"),
    session_open_hour=3,
    session_close_hour=12,
)
strategy = DualThrust(config)
```

## Limitations

- Session strategies (`DualThrust`, `LondonBreakout`) assume bar `ts_event` is UTC; adjust `session_*_hour` for your data timezone.
- `BollingerBottomW` is a simplified approximation of the full W-pattern scanner.
- Long-only; short signals from source repos are not mapped.
- awesome-systematic-trading itself has no strategies to port — only its linked repos.

## Relationship to freqtrade_ported

```
awesome-systematic-trading (links)
        │
        ├── je-suis-tm/quant-trading ──► systematic_trading_ported/  (new)
        │
        └── freqtrade/freqtrade ──► freqtrade_ported/  (existing)
```

See `dedup.py` for the full cross-reference table.
