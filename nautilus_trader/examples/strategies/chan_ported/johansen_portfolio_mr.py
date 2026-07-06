# -------------------------------------------------------------------------------------------------
#  Copyright (C) 2015-2026 Nautech Systems Pty Ltd. All rights reserved.
#  https://nautechsystems.io
#
#  Licensed under the GNU Lesser General Public License Version 3.0 (the "License");
#  You may not use this file except in compliance with the License.
#  You may obtain a copy of the License at https://www.gnu.org/licenses/lgpl-3.0.en.html
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# -------------------------------------------------------------------------------------------------

"""Chan Example 2.8: Johansen eigenvector portfolio mean reversion (3-leg)."""

from collections import deque
from decimal import Decimal

import pandas as pd

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.config import StrategyConfig
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import TimeInForce
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.trading.strategy import Strategy



class JohansenPortfolioMrConfig(StrategyConfig, frozen=True):
    """Configuration for ``JohansenPortfolioMr`` (EWA-EWC-IGE style)."""

    instrument_ids: tuple[InstrumentId, InstrumentId, InstrumentId]
    bar_types: tuple[BarType, BarType, BarType]
    weights: tuple[float, float, float] = (-0.74, 1.0, -0.24)
    trade_size: Decimal
    lookback: PositiveInt = 20
    entry_z: PositiveFloat = 1.0
    exit_z: PositiveFloat = 0.0
    request_historical_bars: bool = True
    historical_bars_days: PositiveInt = 400
    close_positions_on_stop: bool = True


class JohansenPortfolioMr(Strategy):
    """
    Linear mean reversion on a weighted 3-ETF portfolio (Johansen eigenvector).

    Chan (2013) Examples 2.7-2.8, Ch.2 p.76. Default weights approximate the
  EWA-EWC-IGE eigenvector from the book; re-estimate via Johansen offline.
    """

    def __init__(self, config: JohansenPortfolioMrConfig) -> None:
        super().__init__(config)
        self._instruments: list[Instrument | None] = [None, None, None]
        self._last_prices: list[float | None] = [None, None, None]
        self._portfolio_values: deque[float] = deque(maxlen=config.lookback)
        self._position_open: bool = False

    def on_start(self) -> None:
        cfg = self.config
        for i, iid in enumerate(cfg.instrument_ids):
            self._instruments[i] = self.cache.instrument(iid)
            if self._instruments[i] is None:
                self.log.error(f"Missing instrument {iid}")
                self.stop()
                return

        if cfg.request_historical_bars:
            start = self._clock.utc_now() - pd.Timedelta(days=cfg.historical_bars_days)
            pending = set(cfg.bar_types)

            def make_cb(bt: BarType):
                def _cb(_: object) -> None:
                    pending.discard(bt)
                    if not pending:
                        for b in cfg.bar_types:
                            self.subscribe_bars(b)
                return _cb

            for bt in cfg.bar_types:
                self.request_bars(bt, start=start, callback=make_cb(bt))
        else:
            for bt in cfg.bar_types:
                self.subscribe_bars(bt)

    def on_bar(self, bar: Bar) -> None:
        cfg = self.config
        try:
            idx = cfg.bar_types.index(bar.bar_type)
        except ValueError:
            return
        if bar.is_single_price():
            return
        self._last_prices[idx] = bar.close.as_double()
        if any(p is None for p in self._last_prices):
            return

        w = cfg.weights
        pvals = self._last_prices  # type: ignore[list-item]
        port_val = sum(w[i] * pvals[i] for i in range(3))
        self._portfolio_values.append(port_val)

        if len(self._portfolio_values) < cfg.lookback:
            return

        mean = sum(self._portfolio_values) / len(self._portfolio_values)
        var = sum((v - mean) ** 2 for v in self._portfolio_values) / len(self._portfolio_values)
        std = var ** 0.5 if var > 0 else 0.0
        z = (port_val - mean) / std if std > 1e-12 else 0.0

        if not self._position_open:
            if z < -cfg.entry_z:
                self._open_portfolio(long_portfolio=True)
            elif z > cfg.entry_z:
                self._open_portfolio(long_portfolio=False)
        elif abs(z) <= cfg.exit_z:
            self._close_all_legs()
            self._position_open = False

    def _open_portfolio(self, *, long_portfolio: bool) -> None:
        cfg = self.config
        sign = 1.0 if long_portfolio else -1.0
        for i, inst in enumerate(self._instruments):
            if inst is None:
                continue
            w = cfg.weights[i] * sign
            side = OrderSide.BUY if w > 0 else OrderSide.SELL
            self.submit_order(
                self.order_factory.market(
                    cfg.instrument_ids[i],
                    side,
                    inst.make_qty(cfg.trade_size),
                    TimeInForce.GTC,
                ),
            )
        self._position_open = True

    def _close_all_legs(self) -> None:
        for iid in self.config.instrument_ids:
            self.close_all_positions(iid)

    def on_stop(self) -> None:
        if self.config.close_positions_on_stop:
            self._close_all_legs()
        for bt in self.config.bar_types:
            self.unsubscribe_bars(bt)
