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

"""Realized-volatility risk-premium proxy."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.academic_ported.indicators import RealizedVolatility
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class VolRiskPremiumConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``VolRiskPremium``."""

    vol_period: PositiveInt = 21
    vol_sma_period: PositiveInt = 252
    historical_bars_days: PositiveInt = 400


class VolRiskPremium(FreqtradeLongOnlyStrategy):
    """
    Long when realized volatility is below its long-run average.

    Equity proxy for ``volatility-risk-premium-effect.py`` (options leg omitted).
    """

    def __init__(self, config: VolRiskPremiumConfig) -> None:
        super().__init__(config)
        self._vol = RealizedVolatility(config.vol_period)
        self._vol_sma = SimpleMovingAverage(config.vol_sma_period)

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._vol)

    def on_bar(self, bar: Bar) -> None:
        if self._vol.initialized:
            self._vol_sma.update_raw(self._vol.value)
        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        if not self._vol.initialized or not self._vol_sma.initialized:
            return False
        return self._vol.value < self._vol_sma.value

    def check_exit(self, bar: Bar) -> bool:
        if not self._vol.initialized or not self._vol_sma.initialized:
            return False
        return self._vol.value >= self._vol_sma.value
