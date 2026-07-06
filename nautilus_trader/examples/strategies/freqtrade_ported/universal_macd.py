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

"""Port of Freqtrade ``UniversalMACD``."""

from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import UniversalMacdRatio


class UniversalMacdConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``UniversalMacd`` (hyperopt defaults from Freqtrade)."""

    buy_umacd_min: float = -0.01416
    buy_umacd_max: float = -0.01176
    sell_umacd_min: float = -0.02323
    sell_umacd_max: float = -0.00707


class UniversalMacd(FreqtradeLongOnlyStrategy):
    """Universal MACD ratio strategy (ported from Freqtrade UniversalMACD)."""

    def __init__(self, config: UniversalMacdConfig) -> None:
        super().__init__(config)
        self._umacd = UniversalMacdRatio()

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._umacd)

    def check_entry(self, bar: Bar) -> bool:
        return self.config.buy_umacd_min <= self._umacd.value <= self.config.buy_umacd_max

    def check_exit(self, bar: Bar) -> bool:
        return self.config.sell_umacd_min <= self._umacd.value <= self.config.sell_umacd_max
