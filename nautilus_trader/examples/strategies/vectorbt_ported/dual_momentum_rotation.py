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

"""Port of vectorbt ``dual_momentum`` (single-asset absolute momentum)."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import RateOfChange
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class DualMomentumRotationConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``DualMomentumRotation``."""

    roc_period: PositiveInt = 63
    historical_bars_days: PositiveInt = 120


class DualMomentumRotation(FreqtradeLongOnlyStrategy):
    """
    Long when trailing ROC > 0 (absolute momentum proxy for ETF rotation).

    Multi-asset NIFTYBEES/GOLDBEES rotation from source requires two symbols;
    this single-instrument port keeps the momentum gate only.
    """

    def __init__(self, config: DualMomentumRotationConfig) -> None:
        super().__init__(config)
        self._roc = RateOfChange(config.roc_period)

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._roc)

    def check_entry(self, bar: Bar) -> bool:
        return self._roc.value > 0

    def check_exit(self, bar: Bar) -> bool:
        return self._roc.value <= 0
