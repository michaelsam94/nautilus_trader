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

"""Port of Freqtrade ``hlhb``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import ExponentialMovingAverage
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_from_freqtrade
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import AverageDirectionalIndex


class HlhbConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``Hlhb`` (HLHB forex system)."""

    rsi_period: PositiveInt = 10
    ema_fast_period: PositiveInt = 5
    ema_slow_period: PositiveInt = 10
    adx_period: PositiveInt = 14
    adx_threshold: PositiveFloat = 25.0
    rsi_midline: PositiveFloat = 50.0


class Hlhb(FreqtradeLongOnlyStrategy):
    """HLHB momentum system (ported from Freqtrade hlhb)."""

    def __init__(self, config: HlhbConfig) -> None:
        super().__init__(config)
        self._rsi = RelativeStrengthIndex(config.rsi_period)
        self._ema5 = ExponentialMovingAverage(config.ema_fast_period)
        self._ema10 = ExponentialMovingAverage(config.ema_slow_period)
        self._adx = AverageDirectionalIndex(config.adx_period)
        self._rsi_cross = CrossDetector()
        self._ema_cross = CrossDetector()
        self._rsi_exit_cross = CrossDetector()
        self._ema_exit_cross = CrossDetector()

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        self.register_indicator_for_bars(bar_type, self._rsi)
        self.register_indicator_for_bars(bar_type, self._ema5)
        self.register_indicator_for_bars(bar_type, self._ema10)
        self.register_indicator_for_bars(bar_type, self._adx)

    def check_entry(self, bar: Bar) -> bool:
        rsi_mid = rsi_from_freqtrade(self.config.rsi_midline)
        return (
            self._rsi_cross.crossed_above(self._rsi.value, rsi_mid)
            and self._ema_cross.crossed_above(self._ema5.value, self._ema10.value)
            and self._adx.adx > self.config.adx_threshold
            and self.bar_volume(bar) > 0
        )

    def check_exit(self, bar: Bar) -> bool:
        rsi_mid = rsi_from_freqtrade(self.config.rsi_midline)
        return (
            self._rsi_exit_cross.crossed_below(self._rsi.value, rsi_mid)
            and self._ema_exit_cross.crossed_below(self._ema5.value, self._ema10.value)
            and self._adx.adx > self.config.adx_threshold
            and self.bar_volume(bar) > 0
        )
