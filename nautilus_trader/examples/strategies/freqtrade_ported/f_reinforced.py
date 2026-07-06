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

"""Port of Freqtrade ``futures/FReinforcedStrategy``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import ExponentialMovingAverage
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongShortStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import AverageDirectionalIndex


class FReinforcedConfig(FreqtradePortConfig, frozen=True, kw_only=True):
    """Configuration for ``FReinforced`` (hyperopt defaults)."""

    trend_bar_type: BarType
    trend_sma_period: PositiveInt = 50
    adx_period: PositiveInt = 14
    ema_short_period: PositiveInt = 8
    ema_long_period: PositiveInt = 21
    exit_adx: PositiveFloat = 30.0


class FReinforced(FreqtradeLongShortStrategy):
    """
    EMA crossover with higher-TF SMA filter (ported from FReinforcedStrategy).

    ``trend_bar_type`` approximates 12x resample (e.g. 60m when primary is 5m).
    """

    def __init__(self, config: FReinforcedConfig) -> None:
        super().__init__(config)
        self._adx = AverageDirectionalIndex(config.adx_period)
        self._ema_short = ExponentialMovingAverage(config.ema_short_period)
        self._ema_long = ExponentialMovingAverage(config.ema_long_period)
        self._trend_sma = SimpleMovingAverage(config.trend_sma_period)
        self._long_cross = CrossDetector()
        self._short_cross = CrossDetector()
        self._trend_close: float = 0.0

    def _register_indicators(self) -> None:
        primary = self.port_config.bar_type
        self.register_indicator_for_bars(primary, self._adx)
        self.register_indicator_for_bars(primary, self._ema_short)
        self.register_indicator_for_bars(primary, self._ema_long)
        self.register_indicator_for_bars(self.config.trend_bar_type, self._trend_sma)

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type == self.config.trend_bar_type:
            self._trend_close = bar.close.as_double()
            return
        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        return (
            close > self._trend_sma.value
            and self._trend_close > self._trend_sma.value
            and self._long_cross.crossed_above(self._ema_short.value, self._ema_long.value)
        )

    def check_entry_short(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        return (
            close < self._trend_sma.value
            and self._trend_close < self._trend_sma.value
            and self._short_cross.crossed_below(self._ema_short.value, self._ema_long.value)
        )

    def check_exit(self, bar: Bar) -> bool:
        return self._adx.adx < self.config.exit_adx

    def check_exit_short(self, bar: Bar) -> bool:
        return self._adx.adx < self.config.exit_adx
