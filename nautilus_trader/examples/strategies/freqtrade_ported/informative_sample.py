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

"""Port of Freqtrade ``InformativeSample``."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import ExponentialMovingAverage
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class InformativeSampleConfig(FreqtradePortConfig, frozen=True, kw_only=True):
    """Configuration for ``InformativeSample``."""

    informative_bar_type: BarType
    ema_fast_period: PositiveInt = 20
    ema_slow_period: PositiveInt = 50
    informative_sma_period: PositiveInt = 20


class InformativeSample(FreqtradeLongOnlyStrategy):
    """
    Informative pair sample (ported from Freqtrade InformativeSample).

    Set ``informative_bar_type`` to the reference pair/timeframe (e.g. BTC 15m)
    and include it in ``informative_bar_types``.
    """

    def __init__(self, config: InformativeSampleConfig) -> None:
        super().__init__(config)
        self._ema20 = ExponentialMovingAverage(config.ema_fast_period)
        self._ema50 = ExponentialMovingAverage(config.ema_slow_period)
        self._informative_sma = SimpleMovingAverage(config.informative_sma_period)
        self._informative_close: float = 0.0

    def _register_indicators(self) -> None:
        primary = self.port_config.bar_type
        self.register_indicator_for_bars(primary, self._ema20)
        self.register_indicator_for_bars(primary, self._ema50)
        self.register_indicator_for_bars(
            self.config.informative_bar_type,
            self._informative_sma,
        )

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type == self.config.informative_bar_type:
            self._informative_close = bar.close.as_double()
            return
        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        return (
            self._ema20.value > self._ema50.value
            and self._informative_close > self._informative_sma.value
        )

    def check_exit(self, bar: Bar) -> bool:
        return (
            self._ema20.value < self._ema50.value
            and self._informative_close < self._informative_sma.value
        )
