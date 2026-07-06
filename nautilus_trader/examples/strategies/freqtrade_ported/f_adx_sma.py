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

"""Port of Freqtrade ``futures/FAdxSmaStrategy``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongShortStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import AverageDirectionalIndex


class FAdxSmaConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``FAdxSma`` (hyperopt defaults)."""

    adx_period: PositiveInt = 14
    sma_short_period: PositiveInt = 12
    sma_long_period: PositiveInt = 48
    entry_adx: PositiveFloat = 30.0
    exit_adx: PositiveFloat = 30.0


class FAdxSma(FreqtradeLongShortStrategy):
    """ADX + SMA crossover futures strategy (ported from FAdxSmaStrategy)."""

    def __init__(self, config: FAdxSmaConfig) -> None:
        super().__init__(config)
        self._adx = AverageDirectionalIndex(config.adx_period)
        self._sma_short = SimpleMovingAverage(config.sma_short_period)
        self._sma_long = SimpleMovingAverage(config.sma_long_period)
        self._long_cross = CrossDetector()
        self._short_cross = CrossDetector()

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        self.register_indicator_for_bars(bar_type, self._adx)
        self.register_indicator_for_bars(bar_type, self._sma_short)
        self.register_indicator_for_bars(bar_type, self._sma_long)

    def check_entry(self, bar: Bar) -> bool:
        return (
            self._adx.adx > self.config.entry_adx
            and self._long_cross.crossed_above(self._sma_short.value, self._sma_long.value)
        )

    def check_entry_short(self, bar: Bar) -> bool:
        return (
            self._adx.adx > self.config.entry_adx
            and self._short_cross.crossed_below(self._sma_short.value, self._sma_long.value)
        )

    def check_exit(self, bar: Bar) -> bool:
        return self._adx.adx < self.config.exit_adx

    def check_exit_short(self, bar: Bar) -> bool:
        return self._adx.adx < self.config.exit_adx
