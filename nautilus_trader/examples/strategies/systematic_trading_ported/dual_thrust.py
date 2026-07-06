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

"""Port of je-suis-tm/quant-trading Dual Thrust (via awesome-systematic-trading)."""

from datetime import datetime
from datetime import timezone

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.systematic_trading_ported.indicators import DualThrustRange


class DualThrustConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``DualThrust``."""

    range_period: PositiveInt = 5
    range_param: PositiveFloat = 0.5
    session_open_hour: PositiveInt = 3
    session_close_hour: PositiveInt = 12


class DualThrust(FreqtradeLongOnlyStrategy):
    """
    Opening-range breakout using Dual Thrust bands.

    Source: je-suis-tm/quant-trading ``Dual Thrust backtest.py``
    (linked from awesome-systematic-trading Alpha Collections).
    """

    def __init__(self, config: DualThrustConfig) -> None:
        super().__init__(config)
        self._range = DualThrustRange(config.range_period)
        self._upper: float = 0.0
        self._lower: float = 0.0
        self._position_side: int = 0

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._range)

    @staticmethod
    def _bar_hour(bar: Bar) -> int:
        return datetime.fromtimestamp(bar.ts_event / 1e9, tz=timezone.utc).hour

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        hour = self._bar_hour(bar)
        close = bar.close.as_double()
        cfg = self.config

        if hour == cfg.session_open_hour and self._range.initialized:
            self._upper = cfg.range_param * self._range.value + close
            self._lower = -(1.0 - cfg.range_param) * self._range.value + close
            self._position_side = 0

        if hour == cfg.session_close_hour:
            if self.portfolio.is_net_long(self.port_config.instrument_id):
                self.exit_long()
            self._position_side = 0
            return

        if self._upper > 0 and close > self._upper and self._position_side <= 0:
            if self.portfolio.is_flat(self.port_config.instrument_id):
                self.enter_long()
            self._position_side = 1
        elif self._lower != 0 and close < self._lower and self._position_side >= 0:
            if self.portfolio.is_net_long(self.port_config.instrument_id):
                self.exit_long()
            self._position_side = -1

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        return False
