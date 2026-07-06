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

"""Port of Freqtrade ``Strategy001_custom_exit``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import ExponentialMovingAverage
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_from_freqtrade
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import HeikinAshi


class Strategy001CustomExitConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``Strategy001CustomExit``."""

    ema_fast_period: PositiveInt = 20
    ema_mid_period: PositiveInt = 50
    ema_slow_period: PositiveInt = 100
    custom_exit_rsi: PositiveFloat = 70.0


class Strategy001CustomExit(FreqtradeLongOnlyStrategy):
    """
    Strategy001 with RSI profit custom exit (ported from Strategy001_custom_exit).

    ``custom_exit`` mapped to ``check_custom_exit`` when unrealized return > 0.
    """

    def __init__(self, config: Strategy001CustomExitConfig) -> None:
        super().__init__(config)
        self._ema20 = ExponentialMovingAverage(config.ema_fast_period)
        self._ema50 = ExponentialMovingAverage(config.ema_mid_period)
        self._ema100 = ExponentialMovingAverage(config.ema_slow_period)
        self._ha = HeikinAshi()
        self._rsi = RelativeStrengthIndex(14)
        self._entry_cross = CrossDetector()
        self._exit_cross = CrossDetector()

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        for ind in (self._ema20, self._ema50, self._ema100, self._ha, self._rsi):
            self.register_indicator_for_bars(bar_type, ind)

    def check_entry(self, bar: Bar) -> bool:
        return (
            self._entry_cross.crossed_above(self._ema20.value, self._ema50.value)
            and self._ha.close > self._ema20.value
            and self._ha.is_green()
        )

    def check_exit(self, bar: Bar) -> bool:
        return (
            self._exit_cross.crossed_above(self._ema50.value, self._ema100.value)
            and self._ha.close < self._ema20.value
            and self._ha.is_red()
        )

    def check_custom_exit(self, bar: Bar) -> bool:
        pnl = self.unrealized_return(bar)
        if pnl is None or pnl <= 0:
            return False
        return self._rsi.value > rsi_from_freqtrade(self.config.custom_exit_rsi)
