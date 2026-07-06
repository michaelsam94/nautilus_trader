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

"""Port of Freqtrade ``berlinguyinca/Quickie``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import BollingerBands
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import ShiftedValue
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import AverageDirectionalIndex
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import TripleExponentialMovingAverage


class QuickieConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``Quickie``."""

    tema_period: PositiveInt = 9
    sma_trend_period: PositiveInt = 200
    adx_entry_threshold: PositiveFloat = 30.0
    adx_exit_threshold: PositiveFloat = 70.0
    bb_period: PositiveInt = 20
    bb_std: PositiveFloat = 2.0


class Quickie(FreqtradeLongOnlyStrategy):
    """TEMA + ADX + Bollinger momentum scalp (ported from Freqtrade Quickie)."""

    def __init__(self, config: QuickieConfig) -> None:
        super().__init__(config)
        self._tema = TripleExponentialMovingAverage(config.tema_period)
        self._sma = SimpleMovingAverage(config.sma_trend_period)
        self._adx = AverageDirectionalIndex(14)
        self._bb = BollingerBands(config.bb_period, config.bb_std)
        self._prev_tema = ShiftedValue()

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        self.register_indicator_for_bars(bar_type, self._tema)
        self.register_indicator_for_bars(bar_type, self._sma)
        self.register_indicator_for_bars(bar_type, self._adx)
        self.register_indicator_for_bars(bar_type, self._bb)

    def check_entry(self, bar: Bar) -> bool:
        prev_tema = self._prev_tema.update(self._tema.value)
        close = bar.close.as_double()
        return (
            self._adx.adx > self.config.adx_entry_threshold
            and self._tema.value < self._bb.middle
            and prev_tema is not None
            and self._tema.value > prev_tema
            and self._sma.value > close
        )

    def check_exit(self, bar: Bar) -> bool:
        prev_tema = self._prev_tema.update(self._tema.value)
        return (
            self._adx.adx > self.config.adx_exit_threshold
            and self._tema.value > self._bb.middle
            and prev_tema is not None
            and self._tema.value < prev_tema
        )
