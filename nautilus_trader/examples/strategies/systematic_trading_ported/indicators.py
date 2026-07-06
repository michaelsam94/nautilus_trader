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

"""Additional indicators for systematic-trading ports."""

from __future__ import annotations

from collections import deque

from nautilus_trader.core.correctness import PyCondition
from nautilus_trader.indicators import Indicator
from nautilus_trader.model.data import Bar


class ParabolicSar(Indicator):
    """
    Parabolic Stop and Reverse (Wilder).

    ``value`` is the SAR level; ``trend`` is +1 (uptrend) or -1 (downtrend).
  Ported from je-suis-tm/quant-trading Parabolic SAR backtest.
    """

    def __init__(
        self,
        initial_af: float = 0.02,
        step_af: float = 0.02,
        end_af: float = 0.2,
    ) -> None:
        super().__init__(params=[initial_af, step_af, end_af])
        self.initial_af = initial_af
        self.step_af = step_af
        self.end_af = end_af
        self.value: float = 0.0
        self.real_sar: float = 0.0
        self.trend: int = 0
        self._ep: float = 0.0
        self._prev_ep: float = 0.0
        self._af: float = initial_af
        self._prev_high: float | None = None
        self._prev_low: float | None = None
        self._prev_high2: float | None = None
        self._prev_low2: float | None = None
        self._bar_count = 0

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        high = bar.high.as_double()
        low = bar.low.as_double()
        close = bar.close.as_double()
        self._bar_count += 1

        if self._bar_count == 1:
            self._prev_high = high
            self._prev_low = low
            self._set_has_inputs(True)
            return

        if self._bar_count == 2:
            self.trend = 1 if close > self._prev_high else -1
            self.value = self._prev_low if self.trend > 0 else self._prev_high
            self.real_sar = self.value
            self._ep = high if self.trend > 0 else low
            self._af = self.initial_af
            self._prev_high2 = self._prev_high
            self._prev_low2 = self._prev_low
            self._prev_high = high
            self._prev_low = low
            return

        assert self._prev_high is not None and self._prev_low is not None
        assert self._prev_high2 is not None and self._prev_low2 is not None

        temp = self.value + self._af * (self._ep - self.value)
        if self.trend < 0:
            self.value = max(temp, self._prev_high, self._prev_high2)
            if self.value < high:
                self.trend = -1
            else:
                self.trend = 1
        else:
            self.value = min(temp, self._prev_low, self._prev_low2)
            if self.value > low:
                self.trend = 1
            else:
                self.trend = -1

        if self.trend < 0:
            if self.trend != -1:
                self._ep = min(low, self._ep)
            else:
                self._ep = low
        else:
            if self.trend != 1:
                self._ep = max(high, self._ep)
            else:
                self._ep = high

        if abs(self.trend) == 1:
            self.real_sar = self._ep
            self._af = self.initial_af
        else:
            self.real_sar = self.value
            if self._ep == self._prev_ep:
                self._af = self._af
            else:
                self._af = min(self.end_af, self._af + self.step_af)

        self._prev_ep = self._ep

        self._prev_high2 = self._prev_high
        self._prev_low2 = self._prev_low
        self._prev_high = high
        self._prev_low = low

        if not self.initialized and self._bar_count >= 3:
            self._set_initialized(True)

    def _reset(self) -> None:
        self.value = 0.0
        self.real_sar = 0.0
        self.trend = 0
        self._ep = 0.0
        self._af = self.initial_af
        self._prev_high = None
        self._prev_low = None
        self._prev_high2 = None
        self._prev_low2 = None
        self._bar_count = 0


class DualThrustRange(Indicator):
    """
    Rolling Dual Thrust range from prior N daily bars.

    Range = max(high_Nmax - close_Nmin, close_Nmax - low_Nmin).
    """

    def __init__(self, period: int = 5) -> None:
        PyCondition.positive_int(period, "period")
        super().__init__(params=[period])
        self.period = period
        self.value: float = 0.0
        self._daily_highs: deque[float] = deque(maxlen=period)
        self._daily_lows: deque[float] = deque(maxlen=period)
        self._daily_closes: deque[float] = deque(maxlen=period)
        self._current_day: int | None = None
        self._day_high: float = 0.0
        self._day_low: float = 0.0
        self._day_close: float = 0.0

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        day = bar.ts_event // (86_400_000_000_000)
        high = bar.high.as_double()
        low = bar.low.as_double()
        close = bar.close.as_double()

        if self._current_day is None:
            self._current_day = day
            self._day_high = high
            self._day_low = low
            self._day_close = close
            self._set_has_inputs(True)
            return

        if day != self._current_day:
            self._daily_highs.append(self._day_high)
            self._daily_lows.append(self._day_low)
            self._daily_closes.append(self._day_close)
            self._current_day = day
            self._day_high = high
            self._day_low = low
            self._day_close = close
            if len(self._daily_highs) >= self.period:
                range1 = max(self._daily_highs) - min(self._daily_closes)
                range2 = max(self._daily_closes) - min(self._daily_lows)
                self.value = max(range1, range2)
                self._set_initialized(True)
        else:
            self._day_high = max(self._day_high, high)
            self._day_low = min(self._day_low, low)
            self._day_close = close

    def _reset(self) -> None:
        self.value = 0.0
        self._daily_highs.clear()
        self._daily_lows.clear()
        self._daily_closes.clear()
        self._current_day = None
        self._day_high = 0.0
        self._day_low = 0.0
        self._day_close = 0.0
