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

"""Port of Freqtrade ``futures/FSampleStrategy``."""

from nautilus_trader.indicators import BollingerBands
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongShortStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import ShiftedValue
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_from_freqtrade
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import TripleExponentialMovingAverage


class FSampleConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``FSample`` futures sample."""


class FSample(FreqtradeLongShortStrategy):
    """
    RSI + TEMA + BB futures sample (ported from FSampleStrategy).

    Hilbert sine indicators from upstream omitted (unused in signals).
    """

    def __init__(self, config: FSampleConfig) -> None:
        super().__init__(config)
        self._rsi = RelativeStrengthIndex(14)
        self._bb = BollingerBands(20, 2.0)
        self._tema = TripleExponentialMovingAverage(9)
        self._rsi_cross_30 = CrossDetector()
        self._rsi_cross_70 = CrossDetector()
        self._prev_tema = ShiftedValue()

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        self.register_indicator_for_bars(bar_type, self._rsi)
        self.register_indicator_for_bars(bar_type, self._bb)
        self.register_indicator_for_bars(bar_type, self._tema)

    def _tema_rising(self) -> bool:
        prev = self._prev_tema.update(self._tema.value)
        return prev is not None and self._tema.value > prev

    def _tema_falling(self) -> bool:
        prev = self._prev_tema.update(self._tema.value)
        return prev is not None and self._tema.value < prev

    def check_entry(self, bar: Bar) -> bool:
        return (
            self._rsi_cross_30.crossed_above_level(self._rsi.value, rsi_from_freqtrade(30.0))
            and self._tema.value <= self._bb.middle
            and self._tema_rising()
            and self.bar_volume(bar) > 0
        )

    def check_entry_short(self, bar: Bar) -> bool:
        return (
            self._rsi_cross_70.crossed_above_level(self._rsi.value, rsi_from_freqtrade(70.0))
            and self._tema.value > self._bb.middle
            and self._tema_falling()
            and self.bar_volume(bar) > 0
        )

    def check_exit(self, bar: Bar) -> bool:
        return (
            self._rsi_cross_70.crossed_above_level(self._rsi.value, rsi_from_freqtrade(70.0))
            and self._tema.value > self._bb.middle
            and self._tema_falling()
            and self.bar_volume(bar) > 0
        )

    def check_exit_short(self, bar: Bar) -> bool:
        return (
            self._rsi_cross_30.crossed_above_level(self._rsi.value, rsi_from_freqtrade(30.0))
            and self._tema.value <= self._bb.middle
            and self._tema_rising()
            and self.bar_volume(bar) > 0
        )
