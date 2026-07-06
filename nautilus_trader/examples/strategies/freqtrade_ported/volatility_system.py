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

"""Port of Freqtrade ``futures/VolatilitySystem``."""

from nautilus_trader.indicators import AverageTrueRange
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongShortStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import ShiftedValue


class VolatilitySystemConfig(FreqtradePortConfig, frozen=True, kw_only=True):
    """
    Configuration for ``VolatilitySystem``.

    ``resample_bar_type`` approximates 3h resampled ATR (e.g. 3h when primary is 1h).
    """

    resample_bar_type: BarType
    atr_multiplier: float = 2.0


class VolatilitySystem(FreqtradeLongShortStrategy):
    """
    Volatility breakout system (ported from VolatilitySystem).

    Position scaling / leverage hooks from upstream not ported.
    """

    def __init__(self, config: VolatilitySystemConfig) -> None:
        super().__init__(config)
        self._atr = AverageTrueRange(14)
        self._prev_close_resample = ShiftedValue()
        self._prev_atr = ShiftedValue()
        self._resample_close: float = 0.0
        self._last_long_signal = False
        self._last_short_signal = False

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.config.resample_bar_type, self._atr)

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type == self.config.resample_bar_type:
            prev = self._prev_close_resample.update(bar.close.as_double())
            self._resample_close = bar.close.as_double()
            if prev is not None and self._atr.initialized:
                change = self._resample_close - prev
                atr = self.config.atr_multiplier * self._atr.value
                prev_atr = self._prev_atr.update(atr)
                if prev_atr is not None:
                    self._last_long_signal = change > prev_atr
                    self._last_short_signal = -change > prev_atr
            return
        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        return self._last_long_signal

    def check_entry_short(self, bar: Bar) -> bool:
        return self._last_short_signal

    def check_exit(self, bar: Bar) -> bool:
        return self._last_short_signal

    def check_exit_short(self, bar: Bar) -> bool:
        return self._last_long_signal
