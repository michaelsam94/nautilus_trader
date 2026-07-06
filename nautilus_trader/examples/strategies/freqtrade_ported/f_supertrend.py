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

"""Port of Freqtrade ``futures/FSupertrendStrategy``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongShortStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import SuperTrend


class FSupertrendConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``FSupertrend`` (futures hyperopt defaults)."""

    buy_m1: PositiveFloat = 1.0
    buy_p1: PositiveInt = 14
    buy_m2: PositiveFloat = 3.0
    buy_p2: PositiveInt = 10
    buy_m3: PositiveFloat = 4.0
    buy_p3: PositiveInt = 10
    sell_m1: PositiveFloat = 1.0
    sell_p1: PositiveInt = 14
    sell_m2: PositiveFloat = 3.0
    sell_p2: PositiveInt = 10
    sell_m3: PositiveFloat = 4.0
    sell_p3: PositiveInt = 10


class FSupertrend(FreqtradeLongShortStrategy):
    """
    Futures SuperTrend long/short (ported from Freqtrade FSupertrendStrategy).

    Requires a short-capable instrument and account in live use.
    """

    def __init__(self, config: FSupertrendConfig) -> None:
        super().__init__(config)
        self._buy1 = SuperTrend(config.buy_p1, config.buy_m1)
        self._buy2 = SuperTrend(config.buy_p2, config.buy_m2)
        self._buy3 = SuperTrend(config.buy_p3, config.buy_m3)
        self._sell1 = SuperTrend(config.sell_p1, config.sell_m1)
        self._sell2 = SuperTrend(config.sell_p2, config.sell_m2)
        self._sell3 = SuperTrend(config.sell_p3, config.sell_m3)

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        for st in (
            self._buy1,
            self._buy2,
            self._buy3,
            self._sell1,
            self._sell2,
            self._sell3,
        ):
            self.register_indicator_for_bars(bar_type, st)

    def check_entry(self, bar: Bar) -> bool:
        return (
            self._buy1.is_up()
            and self._buy2.is_up()
            and self._buy3.is_up()
            and self.bar_volume(bar) > 0
        )

    def check_entry_short(self, bar: Bar) -> bool:
        return (
            self._sell1.is_down()
            and self._sell2.is_down()
            and self._sell3.is_down()
            and self.bar_volume(bar) > 0
        )

    def check_exit(self, bar: Bar) -> bool:
        return self._sell2.is_down()

    def check_exit_short(self, bar: Bar) -> bool:
        return self._buy2.is_up()
