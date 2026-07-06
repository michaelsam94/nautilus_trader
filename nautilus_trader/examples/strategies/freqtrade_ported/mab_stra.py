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

"""Port of Freqtrade ``mabStra`` (hyperopt default parameters)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class MabStraConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``MabStra`` (defaults from hyperopt result block)."""

    buy_mojo: PositiveInt = 7
    buy_fast: PositiveInt = 14
    buy_slow: PositiveInt = 28
    buy_div_min: PositiveFloat = 0.29497
    buy_div_max: PositiveFloat = 2.25446
    sell_mojo: PositiveInt = 7
    sell_fast: PositiveInt = 14
    sell_slow: PositiveInt = 28
    sell_div_min: PositiveFloat = 1.54593
    sell_div_max: PositiveFloat = 2.81436


class MabStra(FreqtradeLongOnlyStrategy):
    """SMA ratio bands strategy (ported from mabStra)."""

    def __init__(self, config: MabStraConfig) -> None:
        super().__init__(config)
        self._buy_mojo = SimpleMovingAverage(config.buy_mojo)
        self._buy_fast = SimpleMovingAverage(config.buy_fast)
        self._buy_slow = SimpleMovingAverage(config.buy_slow)
        self._sell_mojo = SimpleMovingAverage(config.sell_mojo)
        self._sell_fast = SimpleMovingAverage(config.sell_fast)
        self._sell_slow = SimpleMovingAverage(config.sell_slow)

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        for ind in (
            self._buy_mojo,
            self._buy_fast,
            self._buy_slow,
            self._sell_mojo,
            self._sell_fast,
            self._sell_slow,
        ):
            self.register_indicator_for_bars(bar_type, ind)

    def _in_range(self, ratio: float, lo: float, hi: float) -> bool:
        return lo < ratio < hi

    def check_entry(self, bar: Bar) -> bool:
        cfg = self.config
        if self._buy_fast.value == 0 or self._buy_slow.value == 0:
            return False
        r1 = self._buy_mojo.value / self._buy_fast.value
        r2 = self._buy_fast.value / self._buy_slow.value
        return (
            self._in_range(r1, cfg.buy_div_min, cfg.buy_div_max)
            and self._in_range(r2, cfg.buy_div_min, cfg.buy_div_max)
        )

    def check_exit(self, bar: Bar) -> bool:
        cfg = self.config
        if self._sell_mojo.value == 0 or self._sell_fast.value == 0:
            return False
        r1 = self._sell_fast.value / self._sell_mojo.value
        r2 = self._sell_slow.value / self._sell_fast.value
        return (
            self._in_range(r1, cfg.sell_div_min, cfg.sell_div_max)
            and self._in_range(r2, cfg.sell_div_min, cfg.sell_div_max)
        )
