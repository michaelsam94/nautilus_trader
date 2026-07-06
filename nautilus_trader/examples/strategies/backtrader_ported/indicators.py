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

"""Indicators for Backtrader strategy ports."""

from __future__ import annotations

import math
from collections import deque

from nautilus_trader.core.correctness import PyCondition
from nautilus_trader.indicators import AdaptiveMovingAverage
from nautilus_trader.indicators import ExponentialMovingAverage
from nautilus_trader.indicators import Indicator
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar


class ThrustOscillator(Indicator):
    """Thrust oscillator: (fast EMA - KAMA) / KAMA."""

    def __init__(self, kama_period: int = 30, fast_ema_period: int = 7) -> None:
        PyCondition.positive_int(kama_period, "kama_period")
        PyCondition.positive_int(fast_ema_period, "fast_ema_period")
        super().__init__(params=[kama_period, fast_ema_period])
        self._kama = AdaptiveMovingAverage(kama_period)
        self._fast = ExponentialMovingAverage(fast_ema_period)
        self.value: float = 0.0

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        close = bar.close.as_double()
        self._kama.handle_bar(bar)
        self._fast.update_raw(close)
        if not self._kama.initialized or not self._fast.initialized:
            return
        kama = self._kama.value
        self.value = (self._fast.value - kama) / (kama + 1e-6)
        if not self.initialized:
            self._set_has_inputs(True)
            self._set_initialized(True)

    def _reset(self) -> None:
        self._kama.reset()
        self._fast.reset()
        self.value = 0.0


class RollingExtreme(Indicator):
    """Rolling highest high or lowest low over ``period`` bars."""

    def __init__(self, period: int, *, highest: bool = True) -> None:
        PyCondition.positive_int(period, "period")
        super().__init__(params=[period, highest])
        self.period = period
        self.highest = highest
        self.value: float = 0.0
        self._window: deque[float] = deque(maxlen=period)

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        sample = bar.high.as_double() if self.highest else bar.low.as_double()
        self._window.append(sample)
        if len(self._window) < self.period:
            return
        self.value = max(self._window) if self.highest else min(self._window)
        if not self.initialized:
            self._set_has_inputs(True)
            self._set_initialized(True)

    def _reset(self) -> None:
        self._window.clear()
        self.value = 0.0


class OUZScore(Indicator):
    """
    Rolling Ornstein-Uhlenbeck z-score from log-price OLS (ali-azary source).

    Estimates mean reversion speed over ``lookback`` bars and returns
    ``(log_price - mu) / equilibrium_std``.
    """

    def __init__(self, lookback: int = 30) -> None:
        PyCondition.positive_int(lookback, "lookback")
        super().__init__(params=[lookback])
        self.lookback = lookback
        self.z_score: float = 0.0
        self.mu: float = 0.0
        self.equilibrium_std: float = 0.0
        self._log_prices: deque[float] = deque(maxlen=lookback)

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        close = bar.close.as_double()
        if close <= 0:
            return
        self._log_prices.append(math.log(close))
        if len(self._log_prices) < self.lookback:
            return

        prices = list(self._log_prices)
        x_lag = prices[:-1]
        dx = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
        n = len(dx)
        mean_x = sum(x_lag) / n
        mean_dx = sum(dx) / n
        var_x = sum((x - mean_x) ** 2 for x in x_lag)
        if var_x < 1e-12:
            return
        slope = sum((x_lag[i] - mean_x) * (dx[i] - mean_dx) for i in range(n)) / var_x
        intercept = mean_dx - slope * mean_x
        theta = -slope
        if theta <= 1e-6:
            return
        mu = intercept / theta
        residuals = [dx[i] - (intercept + slope * x_lag[i]) for i in range(n)]
        sigma = math.sqrt(sum(r * r for r in residuals) / n)
        eq_std = sigma / math.sqrt(2 * theta)
        if eq_std <= 1e-12:
            return

        self.mu = mu
        self.equilibrium_std = eq_std
        self.z_score = (math.log(close) - mu) / eq_std
        if not self.initialized:
            self._set_has_inputs(True)
            self._set_initialized(True)

    def _reset(self) -> None:
        self._log_prices.clear()
        self.z_score = 0.0
        self.mu = 0.0
        self.equilibrium_std = 0.0


class QuantileChannel(Indicator):
    """
    Rolling quantile regression channel (simplified pinball-loss bands).

    Uses time-index linear trend with upper/lower quantile offsets; falls back
    to rolling quantiles when regression is ill-conditioned.
    """

    def __init__(
        self,
        lookback: int = 30,
        upper_quantile: float = 0.8,
        lower_quantile: float = 0.2,
    ) -> None:
        PyCondition.positive_int(lookback, "lookback")
        super().__init__(params=[lookback, upper_quantile, lower_quantile])
        self.lookback = lookback
        self.upper_quantile = upper_quantile
        self.lower_quantile = lower_quantile
        self.upper: float = 0.0
        self.lower: float = 0.0
        self.trend: float = 0.0
        self.confidence: float = 0.0
        self._prices: deque[float] = deque(maxlen=lookback)

    def _quantile(self, values: list[float], tau: float) -> float:
        ordered = sorted(values)
        idx = tau * (len(ordered) - 1)
        lo = int(math.floor(idx))
        hi = int(math.ceil(idx))
        if lo == hi:
            return ordered[lo]
        weight = idx - lo
        return ordered[lo] * (1 - weight) + ordered[hi] * weight

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        close = bar.close.as_double()
        self._prices.append(close)
        if len(self._prices) < self.lookback:
            return

        prices = list(self._prices)
        n = len(prices)
        times = list(range(n))
        mean_t = sum(times) / n
        mean_p = sum(prices) / n
        var_t = sum((t - mean_t) ** 2 for t in times)
        if var_t < 1e-12:
            return
        slope = sum((times[i] - mean_t) * (prices[i] - mean_p) for i in range(n)) / var_t
        intercept = mean_p - slope * mean_t
        trend = intercept + slope * (n - 1)
        residuals = [prices[i] - (intercept + slope * times[i]) for i in range(n)]
        upper_off = self._quantile(residuals, self.upper_quantile)
        lower_off = self._quantile(residuals, self.lower_quantile)

        self.trend = trend
        self.upper = trend + upper_off
        self.lower = trend + lower_off
        price_std = math.sqrt(sum((p - mean_p) ** 2 for p in prices) / n)
        width = (self.upper - self.lower) / (trend + 1e-8)
        expected_width = 2 * price_std / (mean_p + 1e-8)
        self.confidence = min(1.0, expected_width / (width + 1e-8))

        if not self.initialized:
            self._set_has_inputs(True)
            self._set_initialized(True)

    def _reset(self) -> None:
        self._prices.clear()
        self.upper = 0.0
        self.lower = 0.0
        self.trend = 0.0
        self.confidence = 0.0


class ObvWithSignal(Indicator):
    """On-balance volume with SMA signal line and crossover direction."""

    def __init__(self, ma_period: int = 7) -> None:
        PyCondition.positive_int(ma_period, "ma_period")
        super().__init__(params=[ma_period])
        self._ma = SimpleMovingAverage(ma_period)
        self.obv: float = 0.0
        self.signal: float = 0.0
        self.cross_up: bool = False
        self.cross_down: bool = False
        self._prev_obv: float | None = None
        self._prev_signal: float | None = None
        self._prev_close: float | None = None

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        close = bar.close.as_double()
        volume = float(bar.volume) if bar.volume is not None else 0.0
        if self._prev_close is None:
            self._prev_close = close
            self._set_has_inputs(True)
            return

        if close > self._prev_close:
            self.obv += volume
        elif close < self._prev_close:
            self.obv -= volume
        self._prev_close = close
        self._ma.update_raw(self.obv)
        if not self._ma.initialized:
            return

        self.signal = self._ma.value
        self.cross_up = (
            self._prev_obv is not None
            and self._prev_signal is not None
            and self._prev_obv <= self._prev_signal
            and self.obv > self.signal
        )
        self.cross_down = (
            self._prev_obv is not None
            and self._prev_signal is not None
            and self._prev_obv >= self._prev_signal
            and self.obv < self.signal
        )
        self._prev_obv = self.obv
        self._prev_signal = self.signal
        if not self.initialized:
            self._set_initialized(True)

    def _reset(self) -> None:
        self._ma.reset()
        self.obv = 0.0
        self.signal = 0.0
        self.cross_up = False
        self.cross_down = False
        self._prev_obv = None
        self._prev_signal = None
        self._prev_close = None
