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

"""Python indicators used by ported analyzingalpha strategies."""

from __future__ import annotations

from collections import deque

from nautilus_trader.core.correctness import PyCondition
from nautilus_trader.indicators import Indicator
from nautilus_trader.model.data import Bar


class _WilderRsi:
    """Minimal Wilder RSI over a fed value series (0-100 scale)."""

    def __init__(self, period: int) -> None:
        self.period = period
        self.value: float = 50.0
        self.initialized = False
        self._prev: float | None = None
        self._avg_gain = 0.0
        self._avg_loss = 0.0
        self._count = 0

    def update(self, value: float) -> None:
        if self._prev is None:
            self._prev = value
            return
        change = value - self._prev
        self._prev = value
        gain = max(change, 0.0)
        loss = max(-change, 0.0)
        self._count += 1
        if self._count <= self.period:
            self._avg_gain += gain / self.period
            self._avg_loss += loss / self.period
            if self._count < self.period:
                return
        else:
            p = self.period
            self._avg_gain = (self._avg_gain * (p - 1) + gain) / p
            self._avg_loss = (self._avg_loss * (p - 1) + loss) / p
        if self._avg_loss == 0.0:
            self.value = 100.0
        else:
            self.value = 100.0 - 100.0 / (1.0 + self._avg_gain / self._avg_loss)
        self.initialized = True

    def reset(self) -> None:
        self.__init__(self.period)


class ConnorsRsiComposite(Indicator):
    """
    ConnorsRSI: ``(RSI(close, n1) + RSI(streak, n2) + PercentRank(close change, n3)) / 3``.

    The source Backtrader listing passes ``streak.data`` (close) to the streak
    RSI by mistake; this port computes the streak RSI as Connors documented.
    """

    def __init__(
        self,
        rsi_period: int = 3,
        streak_period: int = 2,
        rank_period: int = 100,
    ) -> None:
        PyCondition.positive_int(rsi_period, "rsi_period")
        PyCondition.positive_int(streak_period, "streak_period")
        PyCondition.positive_int(rank_period, "rank_period")
        super().__init__(params=[rsi_period, streak_period, rank_period])
        self.value: float = 50.0
        self._price_rsi = _WilderRsi(rsi_period)
        self._streak_rsi = _WilderRsi(streak_period)
        self._rank_period = rank_period
        self._prev_close: float | None = None
        self._streak = 0
        self._changes: deque[float] = deque(maxlen=rank_period)

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        close = bar.close.as_double()
        self._set_has_inputs(True)

        if self._prev_close is not None:
            if close > self._prev_close:
                self._streak = max(1, self._streak + 1)
            elif close < self._prev_close:
                self._streak = min(-1, self._streak - 1)
            else:
                self._streak = 0
            change = (close - self._prev_close) / self._prev_close
            self._changes.append(change)
            self._streak_rsi.update(float(self._streak))
        self._prev_close = close
        self._price_rsi.update(close)

        ready = (
            self._price_rsi.initialized
            and self._streak_rsi.initialized
            and len(self._changes) == self._rank_period
        )
        if ready:
            current = self._changes[-1]
            below = sum(1 for c in list(self._changes)[:-1] if c < current)
            percent_rank = 100.0 * below / (self._rank_period - 1)
            self.value = (self._price_rsi.value + self._streak_rsi.value + percent_rank) / 3.0
            self._set_initialized(True)

    def _reset(self) -> None:
        self.value = 50.0
        self._price_rsi.reset()
        self._streak_rsi.reset()
        self._prev_close = None
        self._streak = 0
        self._changes.clear()


class WilderAtr(Indicator):
    """ATR with Wilder smoothing (matches the source notebook's ``wwma`` ATR)."""

    def __init__(self, period: int = 12) -> None:
        PyCondition.positive_int(period, "period")
        super().__init__(params=[period])
        self.period = period
        self.value: float = 0.0
        self._prev_close: float | None = None
        self._count = 0

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        high = bar.high.as_double()
        low = bar.low.as_double()
        close = bar.close.as_double()
        self._set_has_inputs(True)
        if self._prev_close is None:
            tr = high - low
        else:
            tr = max(high - low, abs(high - self._prev_close), abs(low - self._prev_close))
        self._prev_close = close
        self._count += 1
        alpha = 1.0 / self.period
        self.value = tr if self._count == 1 else alpha * tr + (1.0 - alpha) * self.value
        if self._count >= self.period:
            self._set_initialized(True)

    def _reset(self) -> None:
        self.value = 0.0
        self._prev_close = None
        self._count = 0
