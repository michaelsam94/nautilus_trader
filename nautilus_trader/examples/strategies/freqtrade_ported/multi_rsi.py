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

"""Port of Freqtrade ``berlinguyinca/MultiRSI``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_to_freqtrade


class MultiRsiConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``MultiRsi``."""

    short_tf_bar_type: BarType
    long_tf_bar_type: BarType
    sma_fast_period: PositiveInt = 5
    sma_slow_period: PositiveInt = 200
    rsi_offset: PositiveFloat = 20.0


class MultiRsi(FreqtradeLongOnlyStrategy):
    """
    Multi-timeframe RSI (ported from Freqtrade MultiRSI).

    Subscribe ``short_tf_bar_type`` (2x primary) and ``long_tf_bar_type`` (8x primary)
    via ``informative_bar_types``.
    """

    def __init__(self, config: MultiRsiConfig) -> None:
        super().__init__(config)
        self._sma5 = SimpleMovingAverage(config.sma_fast_period)
        self._sma200 = SimpleMovingAverage(config.sma_slow_period)
        self._rsi = RelativeStrengthIndex(14)
        self._rsi_short = RelativeStrengthIndex(14)
        self._rsi_long = RelativeStrengthIndex(14)

    def _register_indicators(self) -> None:
        primary = self.port_config.bar_type
        self.register_indicator_for_bars(primary, self._sma5)
        self.register_indicator_for_bars(primary, self._sma200)
        self.register_indicator_for_bars(primary, self._rsi)
        cfg = self.config
        self.register_indicator_for_bars(cfg.short_tf_bar_type, self._rsi_short)
        self.register_indicator_for_bars(cfg.long_tf_bar_type, self._rsi_long)

    def check_entry(self, bar: Bar) -> bool:
        rsi_100 = rsi_to_freqtrade(self._rsi.value)
        rsi_long = rsi_to_freqtrade(self._rsi_long.value)
        return (
            self._sma5.value >= self._sma200.value
            and rsi_100 < (rsi_long - self.config.rsi_offset)
        )

    def check_exit(self, bar: Bar) -> bool:
        rsi_100 = rsi_to_freqtrade(self._rsi.value)
        rsi_short = rsi_to_freqtrade(self._rsi_short.value)
        rsi_long = rsi_to_freqtrade(self._rsi_long.value)
        return rsi_100 > rsi_short and rsi_100 > rsi_long
