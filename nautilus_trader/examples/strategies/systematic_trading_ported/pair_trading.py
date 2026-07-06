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

"""Port of je-suis-tm/quant-trading pair trading (spread z-score, two legs)."""

from __future__ import annotations

import math
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


class PairTradingConfig(StrategyConfig, frozen=True):
    """Configuration for ``PairTrading``."""

    instrument_id: InstrumentId
    hedge_instrument_id: InstrumentId
    bar_type: BarType
    hedge_bar_type: BarType
    trade_size: Decimal
    bandwidth: PositiveInt = 250
    z_entry: PositiveFloat = 1.0
    request_historical_bars: bool = True
    historical_bars_days: PositiveInt = 400
    close_positions_on_stop: bool = True


class PairTrading(Strategy):
    """
    Cointegration-style spread z-score on two correlated instruments.

    Ported from je-suis-tm/quant-trading ``Pair trading backtest.py``.
    Rolling OLS hedge ratio with simplified Engle-Granger stationarity gate on
    residuals; long spread when z < -entry, short spread when z > entry.
    """

    def __init__(self, config: PairTradingConfig) -> None:
        super().__init__(config)
        self.instrument: Instrument | None = None
        self.hedge_instrument: Instrument | None = None
        self._asset1: deque[float] = deque(maxlen=config.bandwidth)
        self._asset2: deque[float] = deque(maxlen=config.bandwidth)
        self._last_asset2: float | None = None
        self._z_score: float = 0.0
        self._spread_position: int = 0
        self._cointegrated: bool = False
        self._residuals: list[float] = []

    def on_start(self) -> None:
        self.instrument = self.cache.instrument(self.config.instrument_id)
        self.hedge_instrument = self.cache.instrument(self.config.hedge_instrument_id)
        if self.instrument is None or self.hedge_instrument is None:
            self.log.error("Missing instrument for pair trading")
            self.stop()
            return

        if self.config.request_historical_bars:
            start = self._clock.utc_now() - pd.Timedelta(days=self.config.historical_bars_days)
            self.request_bars(
                self.config.bar_type,
                start=start,
                callback=lambda _: self.subscribe_bars(self.config.bar_type),
            )
            self.request_bars(
                self.config.hedge_bar_type,
                start=start,
                callback=lambda _: self.subscribe_bars(self.config.hedge_bar_type),
            )
        else:
            self.subscribe_bars(self.config.bar_type)
            self.subscribe_bars(self.config.hedge_bar_type)

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type != self.config.bar_type:
            if bar.bar_type == self.config.hedge_bar_type:
                self._last_asset2 = bar.close.as_double()
            return
        if self._last_asset2 is None or bar.is_single_price():
            return

        p1 = bar.close.as_double()
        p2 = self._last_asset2
        self._asset1.append(p1)
        self._asset2.append(p2)
        if len(self._asset1) < self.config.bandwidth:
            return

        x = list(self._asset1)
        y = list(self._asset2)
        n = len(x)
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        var_x = sum((xi - mean_x) ** 2 for xi in x)
        if var_x < 1e-12:
            return
        beta = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n)) / var_x
        alpha = mean_y - beta * mean_x
        residuals = [y[i] - (alpha + beta * x[i]) for i in range(n)]
        resid_std = math.sqrt(sum(r * r for r in residuals) / n)
        if resid_std < 1e-12:
            return
        self._residuals = residuals
        self._cointegrated = self._engle_granger_ok(residuals)
        self._z_score = (p2 - (alpha + beta * p1)) / resid_std

        if not self._cointegrated:
            if self._spread_position != 0:
                self._close_spread()
            return

        if self._spread_position == 0:
            if self._z_score > self.config.z_entry:
                self._open_spread(short_leg1=True)
            elif self._z_score < -self.config.z_entry:
                self._open_spread(short_leg1=False)
        elif self._spread_position == 1 and self._z_score < 0:
            self._close_spread()
        elif self._spread_position == -1 and self._z_score > 0:
            self._close_spread()

    @staticmethod
    def _engle_granger_ok(residuals: list[float]) -> bool:
        """Simplified Engle-Granger step-1 gate: mean-reverting residuals."""
        n = len(residuals)
        if n < 30:
            return False
        mean_r = sum(residuals) / n
        var_r = sum((r - mean_r) ** 2 for r in residuals) / n
        if var_r < 1e-12:
            return False
        lag_cov = sum(
            (residuals[i] - mean_r) * (residuals[i - 1] - mean_r) for i in range(1, n)
        ) / (n - 1)
        rho = lag_cov / var_r
        # Stationary if lag-1 autocorrelation is negative (error-correction)
        return rho < -0.05

    def _open_spread(self, *, short_leg1: bool) -> None:
        if self.instrument is None or self.hedge_instrument is None:
            return
        side1 = OrderSide.SELL if short_leg1 else OrderSide.BUY
        side2 = OrderSide.BUY if short_leg1 else OrderSide.SELL
        self.submit_order(
            self.order_factory.market(
                self.config.instrument_id,
                side1,
                self.instrument.make_qty(self.config.trade_size),
                TimeInForce.GTC,
            ),
        )
        self.submit_order(
            self.order_factory.market(
                self.config.hedge_instrument_id,
                side2,
                self.hedge_instrument.make_qty(self.config.trade_size),
                TimeInForce.GTC,
            ),
        )
        self._spread_position = -1 if short_leg1 else 1

    def _close_spread(self) -> None:
        self.close_all_positions(self.config.instrument_id)
        self.close_all_positions(self.config.hedge_instrument_id)
        self._spread_position = 0

    def on_stop(self) -> None:
        if self.config.close_positions_on_stop:
            self._close_spread()
        self.unsubscribe_bars(self.config.bar_type)
        self.unsubscribe_bars(self.config.hedge_bar_type)
