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

"""Low realized-volatility long-only filter."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.academic_ported.indicators import RealizedVolatility
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class LowVolatilityConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``LowVolatility``."""

    vol_period: PositiveInt = 252
    vol_sma_period: PositiveInt = 63
    vol_discount: PositiveFloat = 1.0
    historical_bars_days: PositiveInt = 400


class LowVolatility(FreqtradeLongOnlyStrategy):
    """
    Long when trailing volatility is below its moving average.

    Simplified port of ``low-volatility-factor-effect-in-stocks.py``.
    """

    def __init__(self, config: LowVolatilityConfig) -> None:
        super().__init__(config)
        self._vol = RealizedVolatility(config.vol_period)
        self._vol_sma = SimpleMovingAverage(config.vol_sma_period)

    def _register_indicators(self) -> None:
        bt = self.port_config.bar_type
        self.register_indicator_for_bars(bt, self._vol)

    def on_bar(self, bar: Bar) -> None:
        if self._vol.initialized:
            self._vol_sma.update_raw(self._vol.value)
        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        if not self._vol.initialized or not self._vol_sma.initialized:
            return False
        threshold = self._vol_sma.value * self.config.vol_discount
        return self._vol.value < threshold

    def check_exit(self, bar: Bar) -> bool:
        if not self._vol.initialized or not self._vol_sma.initialized:
            return False
        threshold = self._vol_sma.value * self.config.vol_discount
        return self._vol.value >= threshold
