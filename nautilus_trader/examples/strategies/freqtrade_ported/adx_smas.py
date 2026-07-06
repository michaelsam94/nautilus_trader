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

"""Port of Freqtrade ``berlinguyinca/AdxSmas``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import AverageDirectionalIndex


class AdxSmasConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``AdxSmas``."""

    adx_period: PositiveInt = 14
    sma_short_period: PositiveInt = 3
    sma_long_period: PositiveInt = 6
    adx_entry_threshold: PositiveFloat = 25.0
    adx_exit_threshold: PositiveFloat = 25.0


class AdxSmas(FreqtradeLongOnlyStrategy):
    """ADX filter with SMA crossover (ported from Freqtrade AdxSmas)."""

    def __init__(self, config: AdxSmasConfig) -> None:
        super().__init__(config)
        self._adx = AverageDirectionalIndex(config.adx_period)
        self._sma_short = SimpleMovingAverage(config.sma_short_period)
        self._sma_long = SimpleMovingAverage(config.sma_long_period)
        self._entry_cross = CrossDetector()
        self._exit_cross = CrossDetector()

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        self.register_indicator_for_bars(bar_type, self._adx)
        self.register_indicator_for_bars(bar_type, self._sma_short)
        self.register_indicator_for_bars(bar_type, self._sma_long)

    def check_entry(self, bar: Bar) -> bool:
        return (
            self._adx.adx > self.config.adx_entry_threshold
            and self._entry_cross.crossed_above(self._sma_short.value, self._sma_long.value)
        )

    def check_exit(self, bar: Bar) -> bool:
        return (
            self._adx.adx < self.config.adx_exit_threshold
            and self._exit_cross.crossed_above(self._sma_long.value, self._sma_short.value)
        )
