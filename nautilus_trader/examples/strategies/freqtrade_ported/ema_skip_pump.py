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

"""Port of Freqtrade ``berlinguyinca/EMASkipPump``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import BollingerBands
from nautilus_trader.indicators import ExponentialMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import RollingMean
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import ShiftedValue
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import BollingerBandsOnTypicalPrice
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import RollingMaximum
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import RollingMinimum


class EmaSkipPumpConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``EmaSkipPump``."""

    ema_short: PositiveInt = 5
    ema_medium: PositiveInt = 12
    ema_long: PositiveInt = 21
    volume_period: PositiveInt = 30
    volume_spike_factor: PositiveFloat = 20.0


class EmaSkipPump(FreqtradeLongOnlyStrategy):
    """Pump-filtered EMA + BB reversal (ported from EMASkipPump)."""

    def __init__(self, config: EmaSkipPumpConfig) -> None:
        super().__init__(config)
        self._ema5 = ExponentialMovingAverage(config.ema_short)
        self._ema12 = ExponentialMovingAverage(config.ema_medium)
        self._ema21 = ExponentialMovingAverage(config.ema_long)
        self._bb = BollingerBandsOnTypicalPrice(20, 2.0)
        self._min12 = RollingMinimum(config.ema_medium)
        self._max12 = RollingMaximum(config.ema_medium)
        self._volume_mean = RollingMean(config.volume_period)
        self._prev_volume_mean = ShiftedValue()

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        for ind in (self._ema5, self._ema12, self._ema21, self._bb, self._min12, self._max12):
            self.register_indicator_for_bars(bar_type, ind)

    def on_bar(self, bar: Bar) -> None:
        self._volume_mean.update(self.bar_volume(bar))
        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        prev_vol = self._prev_volume_mean.update(self._volume_mean.value)
        volume_cap = (
            prev_vol * self.config.volume_spike_factor if prev_vol is not None else float("inf")
        )
        close = bar.close.as_double()
        return (
            self.bar_volume(bar) < volume_cap
            and close < self._ema5.value
            and close < self._ema12.value
            and close == self._min12.value
            and close <= self._bb.lower
        )

    def check_exit(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        return (
            close > self._ema5.value
            and close > self._ema12.value
            and close >= self._max12.value
            and close >= self._bb.upper
        )
