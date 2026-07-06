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

"""Port of jesse-ai/example-strategies ``RSI2`` (Larry Connors, long only)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_from_freqtrade


class Rsi2Config(FreqtradePortConfig, frozen=True):
    """Configuration for ``Rsi2``."""

    fast_sma_period: PositiveInt = 5
    slow_sma_period: PositiveInt = 200
    rsi_period: PositiveInt = 2
    rsi_oversold: PositiveFloat = 10.0
    historical_bars_days: PositiveInt = 250


class Rsi2(FreqtradeLongOnlyStrategy):
    """
    Connors RSI(2) mean reversion above SMA200; exit above fast SMA.

    Ported from jesse-ai/example-strategies ``RSI2`` (long-only subset).
    """

    def __init__(self, config: Rsi2Config) -> None:
        super().__init__(config)
        self._fast_sma = SimpleMovingAverage(config.fast_sma_period)
        self._slow_sma = SimpleMovingAverage(config.slow_sma_period)
        self._rsi = RelativeStrengthIndex(config.rsi_period)

    def _register_indicators(self) -> None:
        bt = self.port_config.bar_type
        for ind in (self._fast_sma, self._slow_sma, self._rsi):
            self.register_indicator_for_bars(bt, ind)

    def check_entry(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        cfg = self.config
        return (
            close > self._slow_sma.value
            and self._rsi.value <= rsi_from_freqtrade(cfg.rsi_oversold)
        )

    def check_exit(self, bar: Bar) -> bool:
        return bar.close.as_double() > self._fast_sma.value
