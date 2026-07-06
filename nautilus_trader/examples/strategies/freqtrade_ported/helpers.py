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

"""
Helpers for porting Freqtrade strategies to Nautilus Trader.

Freqtrade/TALib RSI uses 0-100; Nautilus ``RelativeStrengthIndex`` uses 0-1.
"""

from __future__ import annotations

import math
from collections import deque


def rsi_to_freqtrade(value: float) -> float:
    """Convert Nautilus RSI (0-1) to Freqtrade/TALib scale (0-100)."""
    return value * 100.0


def rsi_from_freqtrade(threshold: float) -> float:
    """Convert Freqtrade/TALib RSI threshold (0-100) to Nautilus scale (0-1)."""
    return threshold / 100.0


def stoch_to_freqtrade(value: float) -> float:
    """Convert Nautilus stochastic (0-1) to Freqtrade scale (0-100)."""
    return value * 100.0


def stoch_from_freqtrade(threshold: float) -> float:
    """Convert Freqtrade stochastic threshold (0-100) to Nautilus scale (0-1)."""
    return threshold / 100.0


def fisher_rsi(rsi_100: float) -> float:
    """Inverse Fisher transform on RSI (Freqtrade 0-100 scale)."""
    x = 0.1 * (rsi_100 - 50.0)
    exp_2x = math.exp(2.0 * x)
    return (exp_2x - 1.0) / (exp_2x + 1.0)


def fisher_rsi_norma(rsi_100: float) -> float:
    """Normalized inverse Fisher RSI (0-100 scale)."""
    return 50.0 * (fisher_rsi(rsi_100) + 1.0)


class CrossDetector:
    """Detect indicator crossovers using previous-bar values."""

    def __init__(self) -> None:
        self._prev_fast: float | None = None
        self._prev_slow: float | None = None

    def crossed_above(self, fast: float, slow: float) -> bool:
        if self._prev_fast is None or self._prev_slow is None:
            self._prev_fast = fast
            self._prev_slow = slow
            return False

        result = self._prev_fast <= self._prev_slow and fast > slow
        self._prev_fast = fast
        self._prev_slow = slow
        return result

    def crossed_below(self, fast: float, slow: float) -> bool:
        if self._prev_fast is None or self._prev_slow is None:
            self._prev_fast = fast
            self._prev_slow = slow
            return False

        result = self._prev_fast >= self._prev_slow and fast < slow
        self._prev_fast = fast
        self._prev_slow = slow
        return result

    def crossed_above_level(self, value: float, level: float) -> bool:
        return self.crossed_above(value, level)

    def crossed_below_level(self, value: float, level: float) -> bool:
        return self.crossed_below(value, level)

    def reset(self) -> None:
        self._prev_fast = None
        self._prev_slow = None


class ShiftedValue:
    """Track the previous value of a single series (``shift(1)`` equivalent)."""

    def __init__(self) -> None:
        self._prev: float | None = None

    def update(self, value: float) -> float | None:
        previous = self._prev
        self._prev = value
        return previous

    def reset(self) -> None:
        self._prev = None


class RollingMean:
    """Simple rolling mean for volume or price series."""

    def __init__(self, period: int) -> None:
        self.period = period
        self._window: deque[float] = deque(maxlen=period)
        self.value: float = 0.0
        self.initialized = False

    def update(self, value: float) -> None:
        self._window.append(value)
        self.value = sum(self._window) / len(self._window)
        self.initialized = len(self._window) >= self.period

    def reset(self) -> None:
        self._window.clear()
        self.value = 0.0
        self.initialized = False


class RollingStd:
    """Rolling sample standard deviation."""

    def __init__(self, period: int) -> None:
        self.period = period
        self._window: deque[float] = deque(maxlen=period)
        self.value: float = 0.0
        self.initialized = False

    def update(self, value: float) -> None:
        self._window.append(value)
        n = len(self._window)
        if n < self.period:
            return
        mean = sum(self._window) / n
        variance = sum((x - mean) ** 2 for x in self._window) / n
        self.value = math.sqrt(variance)
        self.initialized = True

    def reset(self) -> None:
        self._window.clear()
        self.value = 0.0
        self.initialized = False


class CloseHistory:
    """Track recent close prices for shift(N) lookups."""

    def __init__(self, size: int = 6) -> None:
        self._closes: deque[float] = deque(maxlen=size)

    def update(self, close: float) -> None:
        self._closes.append(close)

    def shifted(self, shift: int) -> float | None:
        if shift < 0 or len(self._closes) <= shift:
            return None
        return self._closes[-(shift + 1)]

    def reset(self) -> None:
        self._closes.clear()


class OpenHistory:
    """Track recent open prices for shift(N) lookups."""

    def __init__(self, size: int = 8) -> None:
        self._opens: deque[float] = deque(maxlen=size)

    def update(self, open_: float) -> None:
        self._opens.append(open_)

    def shifted(self, shift: int) -> float | None:
        if shift < 0 or len(self._opens) <= shift:
            return None
        return self._opens[-(shift + 1)]

    def reset(self) -> None:
        self._opens.clear()


class AverageHistory:
    """Track (O+H+L+C)/4 for ReinforcedQuickie-style patterns."""

    def __init__(self, size: int = 8) -> None:
        self._values: deque[float] = deque(maxlen=size)

    def update(self, bar: object) -> None:
        o = bar.open.as_double()  # type: ignore[attr-defined]
        h = bar.high.as_double()  # type: ignore[attr-defined]
        l = bar.low.as_double()  # type: ignore[attr-defined]
        c = bar.close.as_double()  # type: ignore[attr-defined]
        self._values.append((o + h + l + c) / 4.0)

    def shifted(self, shift: int) -> float | None:
        if shift < 0 or len(self._values) <= shift:
            return None
        return self._values[-(shift + 1)]

    def reset(self) -> None:
        self._values.clear()


def hour_in_range(hour: int, hour_min: int, hour_max: int) -> bool:
    """Inclusive hour range with midnight wrap when ``hour_min > hour_max``."""
    if hour_min <= hour_max:
        return hour_min <= hour <= hour_max
    return hour >= hour_min or hour <= hour_max
