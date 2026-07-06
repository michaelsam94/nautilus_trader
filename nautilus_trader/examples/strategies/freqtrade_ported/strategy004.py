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

"""Port of Freqtrade ``Strategy004``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import CommodityChannelIndex
from nautilus_trader.indicators import ExponentialMovingAverage
from nautilus_trader.indicators import Stochastics
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import RollingMean
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import ShiftedValue
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import stoch_from_freqtrade
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import AverageDirectionalIndex


class Strategy004Config(FreqtradePortConfig, frozen=True):
    """Configuration for ``Strategy004``."""

    adx_fast_threshold: PositiveFloat = 50.0
    adx_slow_entry_threshold: PositiveFloat = 26.0
    adx_slow_exit_threshold: PositiveFloat = 25.0
    stoch_entry_threshold: PositiveFloat = 20.0
    slow_stoch_entry_threshold: PositiveFloat = 30.0
    stoch_exit_threshold: PositiveFloat = 70.0
    volume_mean_period: PositiveInt = 12
    min_mean_volume: PositiveFloat = 0.75


class Strategy004(FreqtradeLongOnlyStrategy):
    """Dual STOCHF + ADX + volume (ported from Freqtrade Strategy004)."""

    def __init__(self, config: Strategy004Config) -> None:
        super().__init__(config)
        self._adx = AverageDirectionalIndex(14)
        self._slow_adx = AverageDirectionalIndex(35)
        self._cci = CommodityChannelIndex(14)
        self._fast_stoch = Stochastics(5, 3, slowing=3)
        self._slow_stoch = Stochastics(50, 3, slowing=3)
        self._ema5 = ExponentialMovingAverage(5)
        self._volume_mean = RollingMean(config.volume_mean_period)
        self._prev_fast_k = ShiftedValue()
        self._prev_fast_d = ShiftedValue()
        self._prev_slow_k = ShiftedValue()
        self._prev_slow_d = ShiftedValue()
        self._stoch_cross = CrossDetector()

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        for ind in (
            self._adx,
            self._slow_adx,
            self._cci,
            self._fast_stoch,
            self._slow_stoch,
            self._ema5,
        ):
            self.register_indicator_for_bars(bar_type, ind)

    def on_bar(self, bar: Bar) -> None:
        self._volume_mean.update(self.bar_volume(bar))
        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        stoch_lo = stoch_from_freqtrade(self.config.stoch_entry_threshold)
        slow_lo = stoch_from_freqtrade(self.config.slow_stoch_entry_threshold)
        prev_k = self._prev_fast_k.update(self._fast_stoch.value_k)
        prev_d = self._prev_fast_d.update(self._fast_stoch.value_d)
        prev_slow_k = self._prev_slow_k.update(self._slow_stoch.value_k)
        prev_slow_d = self._prev_slow_d.update(self._slow_stoch.value_d)
        if None in (prev_k, prev_d, prev_slow_k, prev_slow_d):
            return False
        return (
            (
                self._adx.adx > self.config.adx_fast_threshold
                or self._slow_adx.adx > self.config.adx_slow_entry_threshold
            )
            and self._cci.value < -100.0
            and prev_k < stoch_lo
            and prev_d < stoch_lo
            and prev_slow_k < slow_lo
            and prev_slow_d < slow_lo
            and prev_k < prev_d
            and self._stoch_cross.crossed_above(self._fast_stoch.value_k, self._fast_stoch.value_d)
            and self._volume_mean.value > self.config.min_mean_volume
            and bar.close.as_double() > 0.00000100
        )

    def check_exit(self, bar: Bar) -> bool:
        stoch_hi = stoch_from_freqtrade(self.config.stoch_exit_threshold)
        prev_k = self._prev_fast_k.update(self._fast_stoch.value_k)
        prev_d = self._prev_fast_d.update(self._fast_stoch.value_d)
        if prev_k is None or prev_d is None:
            return False
        return (
            self._slow_adx.adx < self.config.adx_slow_exit_threshold
            and (self._fast_stoch.value_k > stoch_hi or self._fast_stoch.value_d > stoch_hi)
            and prev_k < prev_d
            and bar.close.as_double() > self._ema5.value
        )
