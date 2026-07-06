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

"""Port of Freqtrade ``Strategy002``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import BollingerBands
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.indicators import Stochastics
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import fisher_rsi
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_to_freqtrade
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import stoch_from_freqtrade
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import BollingerBandsOnTypicalPrice
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import HammerPattern
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import ParabolicSAR


class Strategy002Config(FreqtradePortConfig, frozen=True):
    """Configuration for ``Strategy002``."""

    rsi_buy_threshold: PositiveFloat = 30.0
    stoch_buy_threshold: PositiveFloat = 20.0
    fisher_rsi_exit_threshold: float = 0.3


class Strategy002(FreqtradeLongOnlyStrategy):
    """CDLHAMMER + Fisher RSI + SAR (ported from Freqtrade Strategy002)."""

    def __init__(self, config: Strategy002Config) -> None:
        super().__init__(config)
        self._rsi = RelativeStrengthIndex(14)
        self._stoch = Stochastics(14, 3, slowing=3)
        self._bb = BollingerBandsOnTypicalPrice(20, 2.0)
        self._sar = ParabolicSAR()
        self._hammer = HammerPattern()

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        self.register_indicator_for_bars(bar_type, self._rsi)
        self.register_indicator_for_bars(bar_type, self._stoch)
        self.register_indicator_for_bars(bar_type, self._bb)
        self.register_indicator_for_bars(bar_type, self._sar)
        self.register_indicator_for_bars(bar_type, self._hammer)

    def check_entry(self, bar: Bar) -> bool:
        rsi_100 = rsi_to_freqtrade(self._rsi.value)
        stoch_lo = stoch_from_freqtrade(self.config.stoch_buy_threshold)
        close = bar.close.as_double()
        return (
            rsi_100 < self.config.rsi_buy_threshold
            and self._stoch.value_k < stoch_lo
            and self._bb.lower > close
            and self._hammer.value == 100.0
        )

    def check_exit(self, bar: Bar) -> bool:
        rsi_100 = rsi_to_freqtrade(self._rsi.value)
        close = bar.close.as_double()
        return (
            self._sar.value > close
            and fisher_rsi(rsi_100) > self.config.fisher_rsi_exit_threshold
        )
