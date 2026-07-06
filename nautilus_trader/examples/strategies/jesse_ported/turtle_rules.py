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

"""Port of jesse-ai/example-strategies ``TurtleRules`` (System 1 long only)."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import DonchianChannel
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class TurtleRulesLongConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``TurtleRulesLong``."""

    entry_dc_period: PositiveInt = 20
    exit_dc_period: PositiveInt = 10
    historical_bars_days: PositiveInt = 60


class TurtleRulesLong(FreqtradeLongOnlyStrategy):
    """
    Turtle System 1 Donchian breakout (long only).

    Ported from jesse-ai/example-strategies ``TurtleRules``.
    Pyramiding, ATR stops, and short side omitted.
    """

    def __init__(self, config: TurtleRulesLongConfig) -> None:
        super().__init__(config)
        self._entry_dc = DonchianChannel(config.entry_dc_period)
        self._exit_dc = DonchianChannel(config.exit_dc_period)
        self._last_profitable: bool = False
        self._skip_next: bool = False

    def _register_indicators(self) -> None:
        bt = self.port_config.bar_type
        self.register_indicator_for_bars(bt, self._entry_dc)
        self.register_indicator_for_bars(bt, self._exit_dc)

    def check_entry(self, bar: Bar) -> bool:
        if self._skip_next:
            self._skip_next = False
            return False
        high = bar.high.as_double()
        return high >= self._entry_dc.upper

    def check_exit(self, bar: Bar) -> bool:
        low = bar.low.as_double()
        if low <= self._exit_dc.lower:
            self._last_profitable = True
            self._skip_next = True
            return True
        return False
