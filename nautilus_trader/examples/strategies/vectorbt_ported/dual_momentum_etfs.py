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

"""Port of vectorbt ``dual_momentum`` ETF quarterly rotation (two legs)."""

from __future__ import annotations

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


class DualMomentumEtfRotationConfig(StrategyConfig, frozen=True):
    """Configuration for ``DualMomentumEtfRotation``."""

    instrument_id: InstrumentId
    hedge_instrument_id: InstrumentId
    bar_type: BarType
    hedge_bar_type: BarType
    trade_size: Decimal
    allocation: PositiveFloat = 0.75
    quarter_bars: PositiveInt = 63
    request_historical_bars: bool = True
    historical_bars_days: PositiveInt = 400
    close_positions_on_stop: bool = True


class DualMomentumEtfRotation(Strategy):
    """
    Quarterly dual-momentum rotation between two ETFs (long only).

    Ported from vectorbt-backtesting-skills ``dual_momentum_backtest.py``.
    Each quarter, allocate to the prior quarter's return winner; cash remainder
    stays uninvested (source uses 75% allocation).
    """

    def __init__(self, config: DualMomentumEtfRotationConfig) -> None:
        super().__init__(config)
        self.instrument: Instrument | None = None
        self.hedge_instrument: Instrument | None = None
        self._leg1_closes: deque[float] = deque(maxlen=config.quarter_bars + 1)
        self._leg2_closes: deque[float] = deque(maxlen=config.quarter_bars + 1)
        self._last_leg2: float | None = None
        self._bars_seen = 0
        self._holding: str | None = None

    def on_start(self) -> None:
        self.instrument = self.cache.instrument(self.config.instrument_id)
        self.hedge_instrument = self.cache.instrument(self.config.hedge_instrument_id)
        if self.instrument is None or self.hedge_instrument is None:
            self.log.error("Missing instrument for dual momentum rotation")
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
                self._last_leg2 = bar.close.as_double()
            return
        if self._last_leg2 is None or bar.is_single_price():
            return

        p1 = bar.close.as_double()
        p2 = self._last_leg2
        self._leg1_closes.append(p1)
        self._leg2_closes.append(p2)
        self._bars_seen += 1

        if len(self._leg1_closes) < self.config.quarter_bars + 1:
            return
        if self._bars_seen % self.config.quarter_bars != 0:
            return

        start1 = self._leg1_closes[0]
        start2 = self._leg2_closes[0]
        if start1 <= 0 or start2 <= 0:
            return

        ret1 = p1 / start1 - 1.0
        ret2 = p2 / start2 - 1.0
        winner = self.config.instrument_id if ret1 >= ret2 else self.config.hedge_instrument_id
        if winner == self._holding:
            return

        self._close_all()
        self._holding = winner
        inst = self.instrument if winner == self.config.instrument_id else self.hedge_instrument
        if inst is None:
            return
        self.submit_order(
            self.order_factory.market(
                winner,
                OrderSide.BUY,
                inst.make_qty(self.config.trade_size),
                TimeInForce.GTC,
            ),
        )

    def _close_all(self) -> None:
        self.close_all_positions(self.config.instrument_id)
        self.close_all_positions(self.config.hedge_instrument_id)
        self._holding = None

    def on_stop(self) -> None:
        if self.config.close_positions_on_stop:
            self._close_all()
        self.unsubscribe_bars(self.config.bar_type)
        self.unsubscribe_bars(self.config.hedge_bar_type)
