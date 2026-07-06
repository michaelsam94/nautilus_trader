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

"""Port of marketcalls/vectorbt-backtesting-skills donchian template."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import DonchianChannel
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import ShiftedValue


class DonchianBreakoutConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``DonchianBreakout``."""

    donchian_period: PositiveInt = 20


class DonchianBreakout(FreqtradeLongOnlyStrategy):
    """
    Close crosses above shifted Donchian upper; exit on cross below lower.

    Ported from vectorbt-expert ``assets/donchian/backtest.py``.
    """

    def __init__(self, config: DonchianBreakoutConfig) -> None:
        super().__init__(config)
        self._donchian = DonchianChannel(config.donchian_period)
        self._prev_upper = ShiftedValue()
        self._prev_lower = ShiftedValue()
        self._entry_cross = CrossDetector()
        self._exit_cross = CrossDetector()

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._donchian)

    def check_entry(self, bar: Bar) -> bool:
        prev_upper = self._prev_upper.update(self._donchian.upper)
        if prev_upper is None:
            return False
        close = bar.close.as_double()
        entered = self._entry_cross.crossed_above(close, prev_upper)
        return entered

    def check_exit(self, bar: Bar) -> bool:
        prev_lower = self._prev_lower.update(self._donchian.lower)
        if prev_lower is None:
            return False
        close = bar.close.as_double()
        return self._exit_cross.crossed_below(close, prev_lower)
