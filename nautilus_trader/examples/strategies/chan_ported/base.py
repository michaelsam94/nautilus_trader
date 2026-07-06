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

"""
Base classes for Ernest Chan (2013) strategy ports.

Reuses the Freqtrade port bar-subscription pattern where applicable.
"""

from __future__ import annotations

from abc import abstractmethod
from decimal import Decimal

import pandas as pd

from nautilus_trader.config import PositiveInt
from nautilus_trader.config import StrategyConfig
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import TimeInForce
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.trading.strategy import Strategy


# *** CHAN BOOK PORTS ARE EXAMPLES WITH NO ALPHA ADVANTAGE. ***
# *** NOT INTENDED FOR LIVE TRADING WITH REAL MONEY. ***


class ChanPairConfig(StrategyConfig, frozen=True):
    """Shared configuration for two-leg Chan spread strategies."""

    instrument_id: InstrumentId
    hedge_instrument_id: InstrumentId
    bar_type: BarType
    hedge_bar_type: BarType
    trade_size: Decimal
    request_historical_bars: bool = True
    historical_bars_days: PositiveInt = 400
    close_positions_on_stop: bool = True


class ChanPairSpreadStrategy(Strategy):
    """
    Two-instrument spread strategy base (pairs, Kalman, Bollinger spread).

    Leg 1 is ``instrument_id``; leg 2 is ``hedge_instrument_id``.
    """

    def __init__(self, config: ChanPairConfig) -> None:
        super().__init__(config)
        self.instrument: Instrument | None = None
        self.hedge_instrument: Instrument | None = None
        self._last_hedge_price: float | None = None
        self._last_price1: float | None = None
        self._spread_position: int = 0  # +1 long spread, -1 short spread, 0 flat

    @property
    def pair_config(self) -> ChanPairConfig:
        return self.config  # type: ignore[return-value]

    def on_start(self) -> None:
        self.instrument = self.cache.instrument(self.pair_config.instrument_id)
        self.hedge_instrument = self.cache.instrument(self.pair_config.hedge_instrument_id)
        if self.instrument is None or self.hedge_instrument is None:
            self.log.error("Missing instrument for Chan pair strategy")
            self.stop()
            return
        self._on_pair_start()
        if self.pair_config.request_historical_bars:
            start = self._clock.utc_now() - pd.Timedelta(
                days=self.pair_config.historical_bars_days,
            )
            self.request_bars(
                self.pair_config.bar_type,
                start=start,
                callback=lambda _: self.subscribe_bars(self.pair_config.bar_type),
            )
            self.request_bars(
                self.pair_config.hedge_bar_type,
                start=start,
                callback=lambda _: self.subscribe_bars(self.pair_config.hedge_bar_type),
            )
        else:
            self.subscribe_bars(self.pair_config.bar_type)
            self.subscribe_bars(self.pair_config.hedge_bar_type)

    def _on_pair_start(self) -> None:
        """Override for indicator registration."""

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type == self.pair_config.hedge_bar_type:
            self._last_hedge_price = bar.close.as_double()
            return
        if bar.bar_type != self.pair_config.bar_type:
            return
        if self._last_hedge_price is None or bar.is_single_price():
            return
        self._last_price1 = bar.close.as_double()
        self._update_spread_signal(self._last_price1, self._last_hedge_price)
        if not self._signal_ready():
            return
        self._apply_spread_logic()

    @abstractmethod
    def _update_spread_signal(self, price1: float, price2: float) -> None:
        """Update internal spread signal from latest leg prices."""

    @abstractmethod
    def _signal_ready(self) -> bool:
        """Return True when spread signal is initialized."""

    def _apply_spread_logic(self) -> None:
        entry_long, entry_short, exit_long, exit_short = self._spread_signals()
        if self._spread_position == 0:
            if entry_short:
                self._open_spread(short_leg1=True)
            elif entry_long:
                self._open_spread(short_leg1=False)
        elif self._spread_position == 1 and exit_long:
            self._close_spread()
        elif self._spread_position == -1 and exit_short:
            self._close_spread()

    @abstractmethod
    def _spread_signals(self) -> tuple[bool, bool, bool, bool]:
        """Return (entry_long_spread, entry_short_spread, exit_long, exit_short)."""

    def _open_spread(self, *, short_leg1: bool) -> None:
        if self.instrument is None or self.hedge_instrument is None:
            return
        side1 = OrderSide.SELL if short_leg1 else OrderSide.BUY
        side2 = OrderSide.BUY if short_leg1 else OrderSide.SELL
        self.submit_order(
            self.order_factory.market(
                self.pair_config.instrument_id,
                side1,
                self.instrument.make_qty(self.pair_config.trade_size),
                TimeInForce.GTC,
            ),
        )
        self.submit_order(
            self.order_factory.market(
                self.pair_config.hedge_instrument_id,
                side2,
                # Notional-balance the hedge leg: equal unit quantities only make
                # a spread when both legs trade at similar prices (as in the
                # book's ETF pairs); dissimilar legs need price-ratio sizing
                self.hedge_instrument.make_qty(
                    float(self.pair_config.trade_size)
                    * self._last_price1
                    / self._last_hedge_price,
                ),
                TimeInForce.GTC,
            ),
        )
        self._spread_position = -1 if short_leg1 else 1

    def _close_spread(self) -> None:
        self.close_all_positions(self.pair_config.instrument_id)
        self.close_all_positions(self.pair_config.hedge_instrument_id)
        self._spread_position = 0

    def on_stop(self) -> None:
        if self.pair_config.close_positions_on_stop:
            self._close_spread()
        self.unsubscribe_bars(self.pair_config.bar_type)
        self.unsubscribe_bars(self.pair_config.hedge_bar_type)
