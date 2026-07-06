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

"""Port of Freqtrade ``berlinguyinca/Scalp``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import Stochastics
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import stoch_from_freqtrade
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import AverageDirectionalIndex
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import ExponentialMovingAverageOnHigh


class ScalpConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``Scalp``."""

    ema_period: PositiveInt = 5
    adx_threshold: PositiveFloat = 30.0
    stoch_threshold: PositiveFloat = 30.0
    stoch_exit_threshold: PositiveFloat = 70.0


class Scalp(FreqtradeLongOnlyStrategy):
    """High-frequency scalp strategy (ported from Freqtrade Scalp)."""

    def __init__(self, config: ScalpConfig) -> None:
        super().__init__(config)
        self._ema_high = ExponentialMovingAverageOnHigh(config.ema_period)
        self._adx = AverageDirectionalIndex(14)
        self._stoch = Stochastics(5, 3, slowing=3)
        self._stoch_cross = CrossDetector()
        self._stoch_exit_k = CrossDetector()
        self._stoch_exit_d = CrossDetector()

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        self.register_indicator_for_bars(bar_type, self._ema_high)
        self.register_indicator_for_bars(bar_type, self._adx)
        self.register_indicator_for_bars(bar_type, self._stoch)

    def check_entry(self, bar: Bar) -> bool:
        stoch_lo = stoch_from_freqtrade(self.config.stoch_threshold)
        return (
            bar.open.as_double() < self._ema_high.value
            and self._adx.adx > self.config.adx_threshold
            and self._stoch.value_k < stoch_lo
            and self._stoch.value_d < stoch_lo
            and self._stoch_cross.crossed_above(self._stoch.value_k, self._stoch.value_d)
        )

    def check_exit(self, bar: Bar) -> bool:
        stoch_hi = stoch_from_freqtrade(self.config.stoch_exit_threshold)
        return (
            bar.open.as_double() >= self._ema_high.value
            or self._stoch_exit_k.crossed_above_level(self._stoch.value_k, stoch_hi)
            or self._stoch_exit_d.crossed_above_level(self._stoch.value_d, stoch_hi)
        )
