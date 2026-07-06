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

"""WTI–Brent spread mean reversion (two legs)."""

from __future__ import annotations

from collections import deque
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


class WtiBrentSpreadConfig(StrategyConfig, frozen=True):
    """Configuration for ``WtiBrentSpread``."""

    wti_instrument_id: InstrumentId
    brent_instrument_id: InstrumentId
    bar_type: BarType
    brent_bar_type: BarType
    trade_size: Decimal
    spread_period: PositiveInt = 20
    request_historical_bars: bool = True
    historical_bars_days: PositiveInt = 60
    close_positions_on_stop: bool = True


class WtiBrentSpread(Strategy):
    """
    Mean-revert the WTI minus Brent price spread vs its moving average.

    Simplified port of ``trading-wti-brent-spread.py``.
    """

    def __init__(self, config: WtiBrentSpreadConfig) -> None:
        super().__init__(config)
        self.wti: Instrument | None = None
        self.brent: Instrument | None = None
        self._spreads: deque[float] = deque(maxlen=config.spread_period)
        self._brent_close: float | None = None
        self._position: int = 0

    def on_start(self) -> None:
        self.wti = self.cache.instrument(self.config.wti_instrument_id)
        self.brent = self.cache.instrument(self.config.brent_instrument_id)
        if self.wti is None or self.brent is None:
            self.log.error("Missing instrument for WTI/Brent spread")
            self.stop()
            return

        bar_types = (self.config.bar_type, self.config.brent_bar_type)
        if self.config.request_historical_bars:
            pending: set[BarType] = set(bar_types)
            start = self._clock.utc_now() - pd.Timedelta(days=self.config.historical_bars_days)

            def make_callback(bar_type: BarType):
                def _callback(_: object) -> None:
                    pending.discard(bar_type)
                    if not pending:
                        for bt in bar_types:
                            self.subscribe_bars(bt)
                return _callback

            for bar_type in bar_types:
                self.request_bars(bar_type, start=start, callback=make_callback(bar_type))
        else:
            for bar_type in bar_types:
                self.subscribe_bars(bar_type)

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type == self.config.brent_bar_type:
            self._brent_close = bar.close.as_double()
            return
        if self._brent_close is None or bar.is_single_price():
            return

        spread = bar.close.as_double() - self._brent_close
        self._spreads.append(spread)
        if len(self._spreads) < self.config.spread_period:
            return

        spread_ma = sum(self._spreads) / len(self._spreads)
        if self._position == 0:
            if spread > spread_ma:
                self._open_spread(long_wti=False)
            elif spread < spread_ma:
                self._open_spread(long_wti=True)
        elif self._position == 1 and spread >= spread_ma:
            self._close_spread()
        elif self._position == -1 and spread <= spread_ma:
            self._close_spread()

    def _open_spread(self, *, long_wti: bool) -> None:
        if self.wti is None or self.brent is None:
            return
        wti_side = OrderSide.BUY if long_wti else OrderSide.SELL
        brent_side = OrderSide.SELL if long_wti else OrderSide.BUY
        self.submit_order(
            self.order_factory.market(
                self.config.wti_instrument_id,
                wti_side,
                self.wti.make_qty(self.config.trade_size),
                TimeInForce.GTC,
            ),
        )
        self.submit_order(
            self.order_factory.market(
                self.config.brent_instrument_id,
                brent_side,
                self.brent.make_qty(self.config.trade_size),
                TimeInForce.GTC,
            ),
        )
        self._position = 1 if long_wti else -1

    def _close_spread(self) -> None:
        self.close_all_positions(self.config.wti_instrument_id)
        self.close_all_positions(self.config.brent_instrument_id)
        self._position = 0

    def on_stop(self) -> None:
        if self.config.close_positions_on_stop:
            self._close_spread()
        self.unsubscribe_bars(self.config.bar_type)
        self.unsubscribe_bars(self.config.brent_bar_type)
