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

"""Port of jesse-ai/example-strategies ``MACD_EMA``."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import ExponentialMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import MacdWithSignal


class MacdEmaConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``MacdEma``."""

    ema_period: PositiveInt = 100
    fast_period: PositiveInt = 12
    slow_period: PositiveInt = 26
    signal_period: PositiveInt = 9
    historical_bars_days: PositiveInt = 120


class MacdEma(FreqtradeLongOnlyStrategy):
    """
    MACD above signal with price above EMA filter.

    Ported from jesse-ai/example-strategies ``MACD_EMA``.
    """

    def __init__(self, config: MacdEmaConfig) -> None:
        super().__init__(config)
        self._macd = MacdWithSignal(config.fast_period, config.slow_period, config.signal_period)
        self._ema = ExponentialMovingAverage(config.ema_period)

    def _register_indicators(self) -> None:
        bt = self.port_config.bar_type
        self.register_indicator_for_bars(bt, self._macd)
        self.register_indicator_for_bars(bt, self._ema)

    def check_entry(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        return close > self._ema.value and self._macd.macd > self._macd.signal

    def check_exit(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        return self._macd.macd < self._macd.signal and close < self._ema.value
