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

"""Port of Freqtrade ``GodStra`` (fixed hyperopt genome, simplified indicators)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import KeltnerChannelWidth
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import MoneyFlowIndex


class GodStraConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``GodStra`` partial port (default buy/sell genome)."""

    ichimoku_period: PositiveInt = 26
    buy_real_threshold: PositiveFloat = 0.06295
    sell_mfi_threshold: PositiveFloat = 0.8779


class GodStra(FreqtradeLongOnlyStrategy):
    """
    Genetic mega-strategy with fixed genome (partial port from GodStra).

    ``trend_ichimoku_base`` approximated as Kijun-sen / close; ``trend_kst_diff``
    approximated via MFI / 100 for the default sell genome.
    """

    def __init__(self, config: GodStraConfig) -> None:
        super().__init__(config)
        self._kcw = KeltnerChannelWidth(20, 10)
        self._mfi = MoneyFlowIndex(14)
        self._highs: list[float] = []
        self._lows: list[float] = []
        self._ichimoku_base: float = 0.0

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        self.register_indicator_for_bars(bar_type, self._kcw)
        self.register_indicator_for_bars(bar_type, self._mfi)

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type == self.port_config.bar_type:
            period = self.config.ichimoku_period
            self._highs.append(bar.high.as_double())
            self._lows.append(bar.low.as_double())
            if len(self._highs) > period:
                self._highs.pop(0)
                self._lows.pop(0)
            if len(self._highs) == period:
                self._ichimoku_base = (max(self._highs) + min(self._lows)) / 2.0
        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        if close == 0:
            return False
        ichimoku_ratio = self._ichimoku_base / close
        return ichimoku_ratio < self.config.buy_real_threshold

    def check_exit(self, bar: Bar) -> bool:
        mfi_norm = self._mfi.value / 100.0
        return abs(mfi_norm - self.config.sell_mfi_threshold) < 0.01
