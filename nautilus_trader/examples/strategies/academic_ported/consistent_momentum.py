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

"""Dual-window consistent momentum on one symbol."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.academic_ported.indicators import LaggedReturn
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class ConsistentMomentumConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``ConsistentMomentum``."""

    long_window_days: PositiveInt = 147
    short_window_days: PositiveInt = 126
    skip_days: PositiveInt = 21
    historical_bars_days: PositiveInt = 200


class ConsistentMomentum(FreqtradeLongOnlyStrategy):
    """
    Long when both overlapping momentum windows are positive.

    Simplified port of ``consistent-momentum-strategy.py``.
    """

    def __init__(self, config: ConsistentMomentumConfig) -> None:
        super().__init__(config)
        self._t7_t1 = LaggedReturn(config.long_window_days, config.skip_days)
        self._t6_t0 = LaggedReturn(config.short_window_days, 0)

    def _register_indicators(self) -> None:
        bt = self.port_config.bar_type
        self.register_indicator_for_bars(bt, self._t7_t1)
        self.register_indicator_for_bars(bt, self._t6_t0)

    def check_entry(self, bar: Bar) -> bool:
        return self._t7_t1.value > 0 and self._t6_t0.value > 0

    def check_exit(self, bar: Bar) -> bool:
        return self._t7_t1.value <= 0 or self._t6_t0.value <= 0
