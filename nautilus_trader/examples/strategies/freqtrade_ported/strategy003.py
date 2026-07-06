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

"""Port of Freqtrade ``Strategy003``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import ExponentialMovingAverage
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.indicators import Stochastics
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import fisher_rsi
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_to_freqtrade
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import BollingerBandsOnTypicalPrice
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import MoneyFlowIndex
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import ParabolicSAR


class Strategy003Config(FreqtradePortConfig, frozen=True):
    """Configuration for ``Strategy003``."""

    rsi_buy_threshold: PositiveFloat = 28.0
    mfi_buy_threshold: PositiveFloat = 16.0
    fisher_rsi_entry_threshold: float = -0.94
    fisher_rsi_exit_threshold: float = 0.3
    sma_period: PositiveInt = 40


class Strategy003(FreqtradeLongOnlyStrategy):
    """MFI + Fisher RSI + EMA stack (ported from Freqtrade Strategy003)."""

    def __init__(self, config: Strategy003Config) -> None:
        super().__init__(config)
        self._mfi = MoneyFlowIndex(14)
        self._stoch = Stochastics(14, 3, slowing=3)
        self._rsi = RelativeStrengthIndex(14)
        self._bb = BollingerBandsOnTypicalPrice(20, 2.0)
        self._ema5 = ExponentialMovingAverage(5)
        self._ema10 = ExponentialMovingAverage(10)
        self._ema50 = ExponentialMovingAverage(50)
        self._ema100 = ExponentialMovingAverage(100)
        self._sma = SimpleMovingAverage(config.sma_period)
        self._sar = ParabolicSAR()
        self._ema_cross = CrossDetector()

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        for ind in (
            self._mfi,
            self._stoch,
            self._rsi,
            self._bb,
            self._ema5,
            self._ema10,
            self._ema50,
            self._ema100,
            self._sma,
            self._sar,
        ):
            self.register_indicator_for_bars(bar_type, ind)

    def check_entry(self, bar: Bar) -> bool:
        rsi_100 = rsi_to_freqtrade(self._rsi.value)
        close = bar.close.as_double()
        return (
            0 < rsi_100 < self.config.rsi_buy_threshold
            and close < self._sma.value
            and fisher_rsi(rsi_100) < self.config.fisher_rsi_entry_threshold
            and self._mfi.value < self.config.mfi_buy_threshold
            and (
                self._ema50.value > self._ema100.value
                or self._ema_cross.crossed_above(self._ema5.value, self._ema10.value)
            )
            and self._stoch.value_d > self._stoch.value_k
            and self._stoch.value_d > 0
        )

    def check_exit(self, bar: Bar) -> bool:
        rsi_100 = rsi_to_freqtrade(self._rsi.value)
        close = bar.close.as_double()
        return (
            self._sar.value > close
            and fisher_rsi(rsi_100) > self.config.fisher_rsi_exit_threshold
        )
