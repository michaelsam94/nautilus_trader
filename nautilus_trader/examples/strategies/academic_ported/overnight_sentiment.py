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

"""Overnight anomaly using price and VIX SMA filters."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class OvernightSentimentConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``OvernightSentiment``."""

    vix_bar_type: BarType
    sma_period: PositiveInt = 20
    historical_bars_days: PositiveInt = 60


class OvernightSentiment(FreqtradeLongOnlyStrategy):
    """
    Long when price and VIX are on opposite sides of their moving averages.

    Partial port of ``market-sentiment-and-an-overnight-anomaly.py`` (BMS
    sentiment data and intraday MOC/MOO execution omitted).
    """

    def __init__(self, config: OvernightSentimentConfig) -> None:
        super().__init__(config)
        self._price_sma = SimpleMovingAverage(config.sma_period)
        self._vix_sma = SimpleMovingAverage(config.sma_period)
        self._vix_close: float = 0.0

    def all_bar_types(self) -> tuple[BarType, ...]:
        return (self.port_config.bar_type, self.config.vix_bar_type)

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._price_sma)
        self.register_indicator_for_bars(self.config.vix_bar_type, self._vix_sma)

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type == self.config.vix_bar_type:
            self._vix_close = bar.close.as_double()
            return
        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        if not self._price_sma.initialized or not self._vix_sma.initialized:
            return False
        price = bar.close.as_double()
        return price > self._price_sma.value and self._vix_close < self._vix_sma.value

    def check_exit(self, bar: Bar) -> bool:
        if not self._price_sma.initialized or not self._vix_sma.initialized:
            return False
        price = bar.close.as_double()
        return price <= self._price_sma.value or self._vix_close >= self._vix_sma.value
