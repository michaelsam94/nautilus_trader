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

"""Port of Freqtrade ``berlinguyinca/AverageStrategy``."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import ExponentialMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector


class AverageStrategyConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``AverageStrategy``."""

    ema_short_period: PositiveInt = 8
    ema_long_period: PositiveInt = 21


class AverageStrategy(FreqtradeLongOnlyStrategy):
    """EMA crossover strategy (ported from Freqtrade AverageStrategy)."""

    def __init__(self, config: AverageStrategyConfig) -> None:
        super().__init__(config)
        self._ema_short = ExponentialMovingAverage(config.ema_short_period)
        self._ema_long = ExponentialMovingAverage(config.ema_long_period)
        self._entry_cross = CrossDetector()
        self._exit_cross = CrossDetector()

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        self.register_indicator_for_bars(bar_type, self._ema_short)
        self.register_indicator_for_bars(bar_type, self._ema_long)

    def check_entry(self, bar: Bar) -> bool:
        return (
            self._entry_cross.crossed_above(self._ema_short.value, self._ema_long.value)
            and self.bar_volume(bar) > 0
        )

    def check_exit(self, bar: Bar) -> bool:
        return (
            self._exit_cross.crossed_above(self._ema_long.value, self._ema_short.value)
            and self.bar_volume(bar) > 0
        )
