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

"""Port of Freqtrade ``Supertrend`` (triple consensus)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import SuperTrend


class SupertrendConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``Supertrend`` (Freqtrade hyperopt defaults)."""

    buy_m1: PositiveFloat = 4.0
    buy_p1: PositiveInt = 8
    buy_m2: PositiveFloat = 7.0
    buy_p2: PositiveInt = 9
    buy_m3: PositiveFloat = 1.0
    buy_p3: PositiveInt = 8
    sell_m1: PositiveFloat = 1.0
    sell_p1: PositiveInt = 16
    sell_m2: PositiveFloat = 3.0
    sell_p2: PositiveInt = 18
    sell_m3: PositiveFloat = 6.0
    sell_p3: PositiveInt = 18


class Supertrend(FreqtradeLongOnlyStrategy):
    """
    Triple SuperTrend consensus entry/exit (ported from Freqtrade Supertrend).

    Uses hyperopt ``buy_params`` / ``sell_params`` defaults from upstream.
    """

    def __init__(self, config: SupertrendConfig) -> None:
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

    def check_exit(self, bar: Bar) -> bool:
        return (
            self._sell1.is_down()
            and self._sell2.is_down()
            and self._sell3.is_down()
            and self.bar_volume(bar) > 0
        )
