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

"""Port of Freqtrade ``Strategy001``."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import ExponentialMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import HeikinAshi


class Strategy001Config(FreqtradePortConfig, frozen=True):
    """Configuration for ``Strategy001``."""

    ema_fast_period: PositiveInt = 20
    ema_mid_period: PositiveInt = 50
    ema_slow_period: PositiveInt = 100


class Strategy001(FreqtradeLongOnlyStrategy):
    """Heikin Ashi + EMA crossover (ported from Freqtrade Strategy001)."""

    def __init__(self, config: Strategy001Config) -> None:
        super().__init__(config)
        self._ema20 = ExponentialMovingAverage(config.ema_fast_period)
        self._ema50 = ExponentialMovingAverage(config.ema_mid_period)
        self._ema100 = ExponentialMovingAverage(config.ema_slow_period)
        self._ha = HeikinAshi()
        self._entry_cross = CrossDetector()
        self._exit_cross = CrossDetector()

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        self.register_indicator_for_bars(bar_type, self._ema20)
        self.register_indicator_for_bars(bar_type, self._ema50)
        self.register_indicator_for_bars(bar_type, self._ema100)
        self.register_indicator_for_bars(bar_type, self._ha)

    def check_entry(self, bar: Bar) -> bool:
        return (
            self._entry_cross.crossed_above(self._ema20.value, self._ema50.value)
            and self._ha.close > self._ema20.value
            and self._ha.is_green()
        )

    def check_exit(self, bar: Bar) -> bool:
        return (
            self._exit_cross.crossed_above(self._ema50.value, self._ema100.value)
            and self._ha.close < self._ema20.value
            and self._ha.is_red()
        )
