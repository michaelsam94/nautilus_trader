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

"""Port of vectorbt-expert ``sda2`` template."""

from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import ShiftedValue
from nautilus_trader.examples.strategies.vectorbt_ported.indicators import SDA2Bands


class Sda2TrendConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``Sda2Trend``."""


class Sda2Trend(FreqtradeLongOnlyStrategy):
    """
    Close crosses above SDA2 upper band entry; lower band cross exit.

    Ported from marketcalls/vectorbt-backtesting-skills ``sda2/backtest.py``.
    """

    def __init__(self, config: Sda2TrendConfig) -> None:
        super().__init__(config)
        self._sda2 = SDA2Bands()
        self._prev_close = ShiftedValue()
        self._prev_upper = ShiftedValue()
        self._prev_lower = ShiftedValue()

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._sda2)

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        close = bar.close.as_double()
        prev_close = self._prev_close.update(close)
        prev_upper = self._prev_upper.update(self._sda2.upper)
        prev_lower = self._prev_lower.update(self._sda2.lower)
        iid = self.port_config.instrument_id

        if self.portfolio.is_net_long(iid):
            if (
                prev_lower is not None
                and prev_close is not None
                and self._sda2.lower > close
                and prev_lower <= prev_close
            ):
                self.exit_long()
        elif (
            prev_close is not None
            and prev_upper is not None
            and close > self._sda2.upper
            and prev_close <= prev_upper
        ):
            self.enter_long()

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        return False
