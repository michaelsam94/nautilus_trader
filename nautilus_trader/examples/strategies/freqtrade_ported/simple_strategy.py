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

"""Port of Freqtrade ``berlinguyinca/Simple``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import BollingerBands
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import ShiftedValue
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_from_freqtrade
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import MacdWithSignal


class SimpleConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``Simple`` (ported from Freqtrade)."""

    rsi_period: PositiveInt = 7
    bb_period: PositiveInt = 12
    bb_std: PositiveFloat = 2.0


class Simple(FreqtradeLongOnlyStrategy):
    """MACD + RSI + rising upper Bollinger band (ported from Freqtrade Simple)."""

    def __init__(self, config: SimpleConfig) -> None:
        super().__init__(config)
        self._macd = MacdWithSignal()
        self._rsi = RelativeStrengthIndex(config.rsi_period)
        self._bb = BollingerBands(config.bb_period, config.bb_std)
        self._bb_upper_shift = ShiftedValue()

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        self.register_indicator_for_bars(bar_type, self._macd)
        self.register_indicator_for_bars(bar_type, self._rsi)
        self.register_indicator_for_bars(bar_type, self._bb)

    def check_entry(self, bar: Bar) -> bool:
        prev_upper = self._bb_upper_shift.update(self._bb.upper)
        return (
            self._macd.macd > 0
            and self._macd.macd > self._macd.signal
            and self._bb.upper > prev_upper
            and self._rsi.value > rsi_from_freqtrade(70.0)
        )

    def check_exit(self, bar: Bar) -> bool:
        return self._rsi.value > rsi_from_freqtrade(80.0)
