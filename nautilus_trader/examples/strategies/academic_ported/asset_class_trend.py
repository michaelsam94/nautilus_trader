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

"""10-month SMA trend filter on a single asset."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class AssetClassTrendConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``AssetClassTrend``."""

    sma_period: PositiveInt = 210
    historical_bars_days: PositiveInt = 300


class AssetClassTrend(FreqtradeLongOnlyStrategy):
    """
    Long when price is above its 10-month simple moving average.

    Single-instrument port of ``asset-class-trend-following.py`` (multi-ETF
    rotation in source).
    """

    def __init__(self, config: AssetClassTrendConfig) -> None:
        super().__init__(config)
        self._sma = SimpleMovingAverage(config.sma_period)

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._sma)

    def check_entry(self, bar: Bar) -> bool:
        return bar.close.as_double() > self._sma.value

    def check_exit(self, bar: Bar) -> bool:
        return bar.close.as_double() <= self._sma.value
