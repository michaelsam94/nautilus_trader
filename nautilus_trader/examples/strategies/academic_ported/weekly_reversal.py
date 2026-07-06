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

"""Weekly mean-reversion buy-the-dip signal."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.academic_ported.indicators import LaggedReturn
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class WeeklyReversalConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``WeeklyReversal``."""

    week_days: PositiveInt = 5
    historical_bars_days: PositiveInt = 30


class WeeklyReversal(FreqtradeLongOnlyStrategy):
    """
    Buy after a negative week; exit after a positive week.

    Simplified port of ``short-term-reversal-with-futures.py`` (volume/OI
    filters omitted).
    """

    def __init__(self, config: WeeklyReversalConfig) -> None:
        super().__init__(config)
        self._weekly = LaggedReturn(config.week_days, 0)

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._weekly)

    def check_entry(self, bar: Bar) -> bool:
        return self._weekly.value < 0

    def check_exit(self, bar: Bar) -> bool:
        return self._weekly.value > 0
