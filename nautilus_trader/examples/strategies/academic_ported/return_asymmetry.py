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

"""Return-asymmetry (IE) long-only filter."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.academic_ported.indicators import ReturnAsymmetryIndex
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class ReturnAsymmetryConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``ReturnAsymmetry``."""

    ie_period: PositiveInt = 260
    max_ie: int = 0
    historical_bars_days: PositiveInt = 400


class ReturnAsymmetry(FreqtradeLongOnlyStrategy):
    """
    Long when the return-asymmetry index is at or below zero.

    Simplified port of ``return-asymmetry-effect-in-commodity-futures.py``.
    """

    def __init__(self, config: ReturnAsymmetryConfig) -> None:
        super().__init__(config)
        self._ie = ReturnAsymmetryIndex(config.ie_period)

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._ie)

    def check_entry(self, bar: Bar) -> bool:
        return self._ie.value <= self.config.max_ie

    def check_exit(self, bar: Bar) -> bool:
        return self._ie.value > self.config.max_ie
