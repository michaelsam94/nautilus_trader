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

"""Port of Freqtrade ``Strategy005``."""

from typing import Literal

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.indicators import Stochastics
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import RollingMean
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import fisher_rsi_norma
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_to_freqtrade
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import AverageDirectionalIndex
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import MacdWithSignal
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import ParabolicSAR


class Strategy005Config(FreqtradePortConfig, frozen=True):
    """Configuration for ``Strategy005`` (hyperopt defaults)."""

    buy_volume_avg: PositiveInt = 150
    buy_rsi: PositiveInt = 26
    buy_fastd: PositiveInt = 1
    buy_fish_rsi_norma: PositiveInt = 5
    sell_rsi: PositiveInt = 74
    sell_minus_di: PositiveInt = 4
    sell_fish_rsi_norma: PositiveInt = 30
    sell_trigger: Literal["rsi-macd-minusdi", "sar-fisherRsi"] = "rsi-macd-minusdi"
    sma_period: PositiveInt = 40
    min_close: PositiveFloat = 0.00000200
    volume_spike_factor: PositiveFloat = 4.0


class Strategy005(FreqtradeLongOnlyStrategy):
    """Hyperopt categorical sell trigger (ported from Freqtrade Strategy005)."""

    def __init__(self, config: Strategy005Config) -> None:
        super().__init__(config)
        self._macd = MacdWithSignal()
        self._adx = AverageDirectionalIndex(14)
        self._rsi = RelativeStrengthIndex(14)
        self._stoch = Stochastics(14, 3, slowing=3)
        self._sar = ParabolicSAR()
        self._sma = SimpleMovingAverage(config.sma_period)
        self._volume_mean = RollingMean(config.buy_volume_avg)
        self._rsi_cross = CrossDetector()

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        for ind in (self._macd, self._adx, self._rsi, self._stoch, self._sar, self._sma):
            self.register_indicator_for_bars(bar_type, ind)

    def on_bar(self, bar: Bar) -> None:
        self._volume_mean.update(self.bar_volume(bar))
        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        rsi_100 = rsi_to_freqtrade(self._rsi.value)
        close = bar.close.as_double()
        return (
            close > self.config.min_close
            and self.bar_volume(bar) > self._volume_mean.value * self.config.volume_spike_factor
            and close < self._sma.value
            and self._stoch.value_d > self._stoch.value_k
            and rsi_100 > self.config.buy_rsi
            and self._stoch.value_d * 100 > self.config.buy_fastd
            and fisher_rsi_norma(rsi_100) < self.config.buy_fish_rsi_norma
        )

    def check_exit(self, bar: Bar) -> bool:
        rsi_100 = rsi_to_freqtrade(self._rsi.value)
        close = bar.close.as_double()
        if self.config.sell_trigger == "rsi-macd-minusdi":
            return (
                self._rsi_cross.crossed_above(rsi_100, float(self.config.sell_rsi))
                and self._macd.macd < 0
                and self._adx.minus_di > self.config.sell_minus_di
            )
        return (
            self._sar.value > close
            and fisher_rsi_norma(rsi_100) > self.config.sell_fish_rsi_norma
        )
