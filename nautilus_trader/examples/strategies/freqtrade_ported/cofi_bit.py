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

"""Port of Freqtrade ``berlinguyinca/CofiBitStrategy``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.indicators import Stochastics
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import stoch_from_freqtrade
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import AverageDirectionalIndex
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import ExponentialMovingAverageOnHigh
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import ExponentialMovingAverageOnLow


class CofiBitConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``CofiBit`` (hyperopt defaults)."""

    buy_fastx: PositiveFloat = 25.0
    buy_adx: PositiveFloat = 25.0
    sell_fastx: PositiveFloat = 75.0


class CofiBit(FreqtradeLongOnlyStrategy):
    """CofiBit STOCHF + ADX strategy (ported from CofiBitStrategy)."""

    def __init__(self, config: CofiBitConfig) -> None:
        super().__init__(config)
        self._ema_low = ExponentialMovingAverageOnLow(5)
        self._ema_high = ExponentialMovingAverageOnHigh(5)
        self._stoch = Stochastics(5, 3, slowing=3)
        self._adx = AverageDirectionalIndex(14)
        self._stoch_cross = CrossDetector()
        self._stoch_k_exit = CrossDetector()
        self._stoch_d_exit = CrossDetector()

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        for ind in (self._ema_low, self._ema_high, self._stoch, self._adx):
            self.register_indicator_for_bars(bar_type, ind)

    def check_entry(self, bar: Bar) -> bool:
        cfg = self.config
        thr = stoch_from_freqtrade(cfg.buy_fastx)
        return (
            bar.open.as_double() < self._ema_low.value
            and self._stoch_cross.crossed_above(self._stoch.value_k, self._stoch.value_d)
            and self._stoch.value_k < thr
            and self._stoch.value_d < thr
            and self._adx.adx > cfg.buy_adx
        )

    def check_exit(self, bar: Bar) -> bool:
        cfg = self.config
        sell_thr = stoch_from_freqtrade(cfg.sell_fastx)
        return (
            bar.open.as_double() >= self._ema_high.value
            or self._stoch_k_exit.crossed_above_level(self._stoch.value_k, sell_thr)
            or self._stoch_d_exit.crossed_above_level(self._stoch.value_d, sell_thr)
        )
