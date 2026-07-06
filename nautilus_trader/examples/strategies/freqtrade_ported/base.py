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
Base classes for Freqtrade-strategy ports.

Ports Freqtrade's ``populate_entry_trend`` / ``populate_exit_trend`` pattern into
Nautilus ``on_bar`` entry/exit checks. Subclasses implement ``check_entry`` and
``check_exit``.
"""

from __future__ import annotations

from abc import abstractmethod
from decimal import Decimal

import pandas as pd

from nautilus_trader.common.enums import LogColor
from nautilus_trader.config import PositiveInt
from nautilus_trader.config import StrategyConfig
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import TimeInForce
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.model.orders import MarketOrder
from nautilus_trader.trading.strategy import Strategy


# *** PORTED FREQTRADE STRATEGIES ARE EXAMPLES WITH NO ALPHA ADVANTAGE. ***
# *** NOT INTENDED FOR LIVE TRADING WITH REAL MONEY. ***


class FreqtradePortConfig(StrategyConfig, frozen=True):
    """
    Shared configuration for ported Freqtrade long-only strategies.

    Parameters
    ----------
    instrument_id : InstrumentId
        The instrument to trade.
    bar_type : BarType
        Primary bar type (maps to Freqtrade ``timeframe``).
    trade_size : Decimal
        Fixed position size per entry.
    request_historical_bars : bool, default True
        Request historical bars on start for indicator warm-up.
    historical_bars_days : int, default 30
        Lookback days for historical bar request.
    close_positions_on_stop : bool, default True
        Flatten open positions when the strategy stops.
    """

    instrument_id: InstrumentId
    bar_type: BarType
    trade_size: Decimal
    request_historical_bars: bool = True
    historical_bars_days: PositiveInt = 30
    close_positions_on_stop: bool = True


class FreqtradeLongOnlyStrategy(Strategy):
    """
    Base class mapping Freqtrade long-only signal logic to Nautilus bar events.

    Subclasses register indicators in ``__init__``, then implement ``check_entry``
    and ``check_exit`` returning booleans. Freqtrade ROI/stoploss/trailing are not
    auto-mapped; implement via Nautilus risk components if needed.
    """

    def __init__(self, config: FreqtradePortConfig) -> None:
        super().__init__(config)
        self.instrument: Instrument | None = None

    @property
    def port_config(self) -> FreqtradePortConfig:
        return self.config  # type: ignore[return-value]

    def on_start(self) -> None:
        self.instrument = self.cache.instrument(self.port_config.instrument_id)
        if self.instrument is None:
            self.log.error(f"Could not find instrument for {self.port_config.instrument_id}")
            self.stop()
            return

        self._register_indicators()

        if self.port_config.request_historical_bars:
            self.request_bars(
                self.port_config.bar_type,
                start=self._clock.utc_now()
                - pd.Timedelta(days=self.port_config.historical_bars_days),
                callback=lambda _: self.subscribe_bars(self.port_config.bar_type),
            )
        else:
            self.subscribe_bars(self.port_config.bar_type)

    def _register_indicators(self) -> None:
        """Override to register indicators; default no-op."""

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        iid = self.port_config.instrument_id
        if self.check_exit(bar):
            if self.portfolio.is_net_long(iid):
                self.exit_long()
            return

        if self.check_entry(bar) and self.portfolio.is_flat(iid):
            self.enter_long()

    @abstractmethod
    def check_entry(self, bar: Bar) -> bool:
        """Return True when Freqtrade ``enter_long`` would be set."""

    @abstractmethod
    def check_exit(self, bar: Bar) -> bool:
        """Return True when Freqtrade ``exit_long`` would be set."""

    def enter_long(self) -> None:
        if self.instrument is None:
            return
        order = self.order_factory.market(
            instrument_id=self.port_config.instrument_id,
            order_side=OrderSide.BUY,
            quantity=self.instrument.make_qty(self.port_config.trade_size),
            time_in_force=TimeInForce.GTC,
        )
        self.submit_order(order)

    def exit_long(self) -> None:
        self.close_all_positions(self.port_config.instrument_id)

    def on_stop(self) -> None:
        self.cancel_all_orders(self.port_config.instrument_id)
        if self.port_config.close_positions_on_stop:
            self.close_all_positions(self.port_config.instrument_id)
        self.unsubscribe_bars(self.port_config.bar_type)

    def bar_volume(self, bar: Bar) -> float:
        return float(bar.volume) if bar.volume is not None else 0.0

    def log_signal(self, bar: Bar, message: str) -> None:
        self.log.info(f"{message} @ {bar.ts_event}", LogColor.CYAN)
