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

"""Port of Freqtrade ``berlinguyinca/ReinforcedAverageStrategy``."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import ExponentialMovingAverage
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector


class ReinforcedAverageConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``ReinforcedAverage``."""

    trend_bar_type: BarType
    ema_short: PositiveInt = 8
    ema_medium: PositiveInt = 21
    trend_sma_period: PositiveInt = 50


class ReinforcedAverage(FreqtradeLongOnlyStrategy):
    """
    EMA crossover with higher-TF SMA filter (ported from ReinforcedAverageStrategy).

    ``trend_bar_type`` approximates the 12x resampled SMA (e.g. 48h when primary is 4h).
    """

    def __init__(self, config: ReinforcedAverageConfig) -> None:
        super().__init__(config)
        self._ema_short = ExponentialMovingAverage(config.ema_short)
        self._ema_medium = ExponentialMovingAverage(config.ema_medium)
        self._trend_sma = SimpleMovingAverage(config.trend_sma_period)
        self._entry_cross = CrossDetector()
        self._exit_cross = CrossDetector()
        self._trend_close: float = 0.0

    def _register_indicators(self) -> None:
        primary = self.port_config.bar_type
        self.register_indicator_for_bars(primary, self._ema_short)
        self.register_indicator_for_bars(primary, self._ema_medium)
        self.register_indicator_for_bars(self.config.trend_bar_type, self._trend_sma)

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type == self.config.trend_bar_type:
            self._trend_close = bar.close.as_double()
            return
        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        return (
            self._entry_cross.crossed_above(self._ema_short.value, self._ema_medium.value)
            and bar.close.as_double() > self._trend_sma.value
            and self._trend_close > self._trend_sma.value
            and self.bar_volume(bar) > 0
        )

    def check_exit(self, bar: Bar) -> bool:
        return (
            self._exit_cross.crossed_above(self._ema_medium.value, self._ema_short.value)
            and self.bar_volume(bar) > 0
        )
