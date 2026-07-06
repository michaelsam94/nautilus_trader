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

"""Port of Freqtrade ``berlinguyinca/CombinedBinHAndCluc``."""

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


class CombinedBinHAndClucConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``CombinedBinHAndCluc``."""

    bb_wide_period: PositiveInt = 40
    cluc_ema_period: PositiveInt = 50
    cluc_lower_factor: PositiveFloat = 0.985
    volume_period: PositiveInt = 30
    volume_spike_factor: PositiveFloat = 20.0


class CombinedBinHAndCluc(FreqtradeLongOnlyStrategy):
    """BinHV45 OR ClucMay72018 combined entry (ported from CombinedBinHAndCluc)."""

    def __init__(self, config: CombinedBinHAndClucConfig) -> None:
        super().__init__(config)
        self._bb_wide = BollingerBands(config.bb_wide_period, 2.0)
        self._bb_cluc = BollingerBandsOnTypicalPrice(20, 2.0)
        self._ema = ExponentialMovingAverage(config.cluc_ema_period)
        self._volume_mean = RollingMean(config.volume_period)
        self._prev_volume_mean = ShiftedValue()
        self._prev_close = ShiftedValue()
        self._prev_lower = ShiftedValue()

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        self.register_indicator_for_bars(bar_type, self._bb_wide)
        self.register_indicator_for_bars(bar_type, self._bb_cluc)
        self.register_indicator_for_bars(bar_type, self._ema)

    def on_bar(self, bar: Bar) -> None:
        self._volume_mean.update(self.bar_volume(bar))
        super().on_bar(bar)

    def _binhv45_entry(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        prev_close = self._prev_close.update(close)
        prev_lower = self._prev_lower.update(self._bb_wide.lower)
        if prev_close is None or prev_lower is None or prev_lower <= 0:
            return False
        bbdelta = abs(self._bb_wide.middle - self._bb_wide.lower)
        closedelta = abs(close - prev_close)
        tail = abs(close - bar.low.as_double())
        return (
            bbdelta > close * 0.008
            and closedelta > close * 0.0175
            and tail < bbdelta * 0.25
            and close < prev_lower
            and close <= prev_close
        )

    def _cluc_entry(self, bar: Bar) -> bool:
        prev_vol = self._prev_volume_mean.update(self._volume_mean.value)
        volume_cap = (
            prev_vol * self.config.volume_spike_factor if prev_vol is not None else float("inf")
        )
        close = bar.close.as_double()
        return (
            close < self._ema.value
            and close < self.config.cluc_lower_factor * self._bb_cluc.lower
            and self.bar_volume(bar) < volume_cap
        )

    def check_entry(self, bar: Bar) -> bool:
        return self._binhv45_entry(bar) or self._cluc_entry(bar)

    def check_exit(self, bar: Bar) -> bool:
        return bar.close.as_double() > self._bb_cluc.middle
