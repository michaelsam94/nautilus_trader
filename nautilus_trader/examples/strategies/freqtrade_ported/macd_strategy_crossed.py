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

"""Port of Freqtrade ``berlinguyinca/MACDStrategy_crossed``."""

from nautilus_trader.indicators import CommodityChannelIndex
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import MacdWithSignal


class MacdStrategyCrossedConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``MacdStrategyCrossed``."""

    buy_cci: float = -50.0
    sell_cci: float = 100.0


class MacdStrategyCrossed(FreqtradeLongOnlyStrategy):
    """MACD crossover with CCI filter (ported from MACDStrategy_crossed)."""

    def __init__(self, config: MacdStrategyCrossedConfig) -> None:
        super().__init__(config)
        self._macd = MacdWithSignal()
        self._cci = CommodityChannelIndex(14)
        self._macd_cross = CrossDetector()

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        self.register_indicator_for_bars(bar_type, self._macd)
        self.register_indicator_for_bars(bar_type, self._cci)

    def check_entry(self, bar: Bar) -> bool:
        crossed = self._macd_cross.crossed_above(self._macd.macd, self._macd.signal)
        return crossed and self._cci.value <= self.config.buy_cci

    def check_exit(self, bar: Bar) -> bool:
        crossed = self._macd_cross.crossed_below(self._macd.macd, self._macd.signal)
        return crossed and self._cci.value >= self.config.sell_cci
