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

"""Port of Freqtrade ``berlinguyinca/MACDStrategy``."""

from nautilus_trader.indicators import CommodityChannelIndex
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import MacdWithSignal


class MacdStrategyConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``MacdStrategy`` (ported from Freqtrade)."""

    buy_cci: float = -48.0
    sell_cci: float = 687.0


class MacdStrategy(FreqtradeLongOnlyStrategy):
    """MACD above signal with CCI filter (ported from Freqtrade MACDStrategy)."""

    def __init__(self, config: MacdStrategyConfig) -> None:
        super().__init__(config)
        self._macd = MacdWithSignal()
        self._cci = CommodityChannelIndex(14)

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        self.register_indicator_for_bars(bar_type, self._macd)
        self.register_indicator_for_bars(bar_type, self._cci)

    def check_entry(self, bar: Bar) -> bool:
        return (
            self._macd.macd > self._macd.signal
            and self._cci.value <= self.config.buy_cci
            and self.bar_volume(bar) > 0
        )

    def check_exit(self, bar: Bar) -> bool:
        return (
            self._macd.macd < self._macd.signal
            and self._cci.value >= self.config.sell_cci
            and self.bar_volume(bar) > 0
        )
