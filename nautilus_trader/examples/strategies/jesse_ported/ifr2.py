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

"""Port of jesse-ai/example-strategies ``IFR2`` (RSI2 + Ichimoku, long only)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import IchimokuCloud
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_from_freqtrade


class Ifr2Config(FreqtradePortConfig, frozen=True):
    """Configuration for ``Ifr2``."""

    rsi_period: PositiveInt = 2
    rsi_entry_threshold: PositiveFloat = 10.0
    tenkan_period: PositiveInt = 20
    kijun_period: PositiveInt = 30
    senkou_period: PositiveInt = 120
    displacement: PositiveInt = 60
    historical_bars_days: PositiveInt = 200


class Ifr2(FreqtradeLongOnlyStrategy):
    """
    RSI(2) oversold above Ichimoku cloud; exit above prior highs.

    Ported from jesse-ai/example-strategies ``IFR2``.
    Hilbert Transform trend filter omitted (no native indicator).
    """

    def __init__(self, config: Ifr2Config) -> None:
        super().__init__(config)
        self._rsi = RelativeStrengthIndex(config.rsi_period)
        self._ichimoku = IchimokuCloud(
            config.tenkan_period,
            config.kijun_period,
            config.senkou_period,
            config.displacement,
        )
        self._highs: list[float] = []

    def _register_indicators(self) -> None:
        bt = self.port_config.bar_type
        self.register_indicator_for_bars(bt, self._rsi)
        self.register_indicator_for_bars(bt, self._ichimoku)

    def on_bar(self, bar: Bar) -> None:
        high = bar.high.as_double()
        self._highs.append(high)
        if len(self._highs) > 4:
            self._highs.pop(0)
        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        cloud_top = max(self._ichimoku.senkou_span_a, self._ichimoku.senkou_span_b)
        return (
            close > cloud_top
            and self._rsi.value < rsi_from_freqtrade(self.config.rsi_entry_threshold)
        )

    def check_exit(self, bar: Bar) -> bool:
        if len(self._highs) < 3:
            return False
        close = bar.close.as_double()
        return close > self._highs[-2] and close > self._highs[-3]
