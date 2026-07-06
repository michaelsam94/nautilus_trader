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

"""Indicators for Ernest Chan (2013) strategy ports."""

from __future__ import annotations

import math
from collections import deque

from nautilus_trader.core.correctness import PyCondition
from nautilus_trader.indicators import Indicator
from nautilus_trader.model.data import Bar


class RollingZScore(Indicator):
    """Rolling z-score of close versus its moving average."""

    def __init__(self, period: int) -> None:
        PyCondition.positive_int(period, "period")
        super().__init__(params=[period])
        self.period = period
        self.value: float = 0.0
        self._closes: deque[float] = deque(maxlen=period)

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        close = bar.close.as_double()
        self._closes.append(close)
        self._set_has_inputs(True)
        if len(self._closes) < self.period:
            return
        mean = sum(self._closes) / self.period
        var = sum((c - mean) ** 2 for c in self._closes) / self.period
        std = math.sqrt(var) if var > 0 else 0.0
        self.value = (close - mean) / std if std > 1e-12 else 0.0
        self._set_initialized(True)


class RollingSpreadZScore(Indicator):
    """
    Z-score of OLS spread between two price series.

  y - (alpha + beta * x) normalized by residual standard deviation.
    """

    def __init__(self, lookback: int) -> None:
        PyCondition.positive_int(lookback, "lookback")
        super().__init__(params=[lookback])
        self.lookback = lookback
        self.value: float = 0.0
        self.hedge_ratio: float = 1.0
        self.alpha: float = 0.0
        self._x: deque[float] = deque(maxlen=lookback)
        self._y: deque[float] = deque(maxlen=lookback)

    def update_prices(self, x: float, y: float) -> None:
        self._x.append(x)
        self._y.append(y)
        self._set_has_inputs(True)
        if len(self._x) < self.lookback:
            return
        xs = list(self._x)
        ys = list(self._y)
        n = len(xs)
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        var_x = sum((xi - mean_x) ** 2 for xi in xs)
        if var_x < 1e-12:
            return
        beta = sum((xs[i] - mean_x) * (ys[i] - mean_y) for i in range(n)) / var_x
        alpha = mean_y - beta * mean_x
        residuals = [ys[i] - (alpha + beta * xs[i]) for i in range(n)]
        resid_std = math.sqrt(sum(r * r for r in residuals) / n)
        if resid_std < 1e-12:
            return
        self.hedge_ratio = beta
        self.alpha = alpha
        spread = y - (alpha + beta * x)
        self.value = spread / resid_std
        self._set_initialized(True)

    def handle_bar(self, bar: Bar) -> None:
        pass  # Updated externally via update_prices for pair feeds


class KalmanHedgeRatio(Indicator):
    """
    Kalman filter for dynamic hedge ratio (Chan Ch.3, Example 3.3).

    State: hedge ratio beta; observation: y_t = beta * x_t + noise.
    """

    def __init__(
        self,
        delta: float = 1e-4,
        observation_variance: float = 1e-3,
    ) -> None:
        super().__init__(params=[delta, observation_variance])
        self.delta = delta
        self.observation_variance = observation_variance
        self.hedge_ratio: float = 0.0
        self.spread: float = 0.0
        self.spread_std: float = 0.0
        self.z_score: float = 0.0
        self._state_cov: float = 1.0
        self._spreads: deque[float] = deque(maxlen=60)

    def update_prices(self, x: float, y: float) -> None:
        if not self.has_inputs:
            self.hedge_ratio = y / x if abs(x) > 1e-12 else 0.0
            self._set_has_inputs(True)
            return

        # Kalman update for time-varying beta
        pred_cov = self._state_cov + self.delta
        obs_var = self.observation_variance
        denom = x * x * pred_cov + obs_var
        if denom < 1e-12:
            return
        kalman_gain = pred_cov * x / denom
        prediction = self.hedge_ratio * x
        innovation = y - prediction
        self.hedge_ratio = self.hedge_ratio + kalman_gain * innovation
        self._state_cov = (1.0 - kalman_gain * x) * pred_cov

        self.spread = y - self.hedge_ratio * x
        self._spreads.append(self.spread)
        if len(self._spreads) >= 20:
            mean_s = sum(self._spreads) / len(self._spreads)
            var_s = sum((s - mean_s) ** 2 for s in self._spreads) / len(self._spreads)
            self.spread_std = math.sqrt(var_s) if var_s > 0 else 0.0
            self.z_score = (
                (self.spread - mean_s) / self.spread_std if self.spread_std > 1e-12 else 0.0
            )
            self._set_initialized(True)

    def handle_bar(self, bar: Bar) -> None:
        pass


def half_life_from_series(values: list[float]) -> float:
    """
    Estimate mean-reversion half-life via AR(1) on lagged series.

    From Chan Example 2.4: half_life = -log(2) / log(rho) for rho < 1.
    """
    n = len(values)
    if n < 10:
        return float(n)
    lagged = values[:-1]
    delta = [values[i + 1] - values[i] for i in range(n - 1)]
    mean_lag = sum(lagged) / len(lagged)
    var_lag = sum((v - mean_lag) ** 2 for v in lagged)
    if var_lag < 1e-12:
        return float(n)
    cov = sum((lagged[i] - mean_lag) * delta[i] for i in range(len(lagged))) / len(lagged)
    rho = 1.0 + cov / var_lag
    if rho >= 1.0 or rho <= 0:
        return float(n)
    return -math.log(2.0) / math.log(rho)


class LogSpreadZScore(Indicator):
    """Z-score on log-price spread with rolling OLS hedge ratio (Example 3.1)."""

    def __init__(self, lookback: int) -> None:
        PyCondition.positive_int(lookback, "lookback")
        super().__init__(params=[lookback])
        self.lookback = lookback
        self.value: float = 0.0
        self.hedge_ratio: float = 1.0
        self._log_x: deque[float] = deque(maxlen=lookback)
        self._log_y: deque[float] = deque(maxlen=lookback)

    def update_prices(self, x: float, y: float) -> None:
        if x <= 0 or y <= 0:
            return
        self._log_x.append(math.log(x))
        self._log_y.append(math.log(y))
        self._set_has_inputs(True)
        if len(self._log_x) < self.lookback:
            return
        xs = list(self._log_x)
        ys = list(self._log_y)
        n = len(xs)
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        var_x = sum((xi - mean_x) ** 2 for xi in xs)
        if var_x < 1e-12:
            return
        beta = sum((xs[i] - mean_x) * (ys[i] - mean_y) for i in range(n)) / var_x
        self.hedge_ratio = beta
        log_spread = sum(
            [-beta, 1.0][j] * v for j, v in enumerate([xs[-1], ys[-1]])
        )
        spreads = [ys[i] - beta * xs[i] for i in range(n)]
        mean_s = sum(spreads) / n
        std_s = math.sqrt(sum((s - mean_s) ** 2 for s in spreads) / n)
        self.value = (log_spread - mean_s) / std_s if std_s > 1e-12 else 0.0
        self._set_initialized(True)

    def handle_bar(self, bar: Bar) -> None:
        pass


class RatioZScore(Indicator):
    """Z-score of price ratio y/x (Chan Example 3.1 ratio variant)."""

    def __init__(self, lookback: int) -> None:
        PyCondition.positive_int(lookback, "lookback")
        super().__init__(params=[lookback])
        self.lookback = lookback
        self.value: float = 0.0
        self._ratios: deque[float] = deque(maxlen=lookback)

    def update_prices(self, x: float, y: float) -> None:
        if abs(x) < 1e-12:
            return
        self._ratios.append(y / x)
        self._set_has_inputs(True)
        if len(self._ratios) < self.lookback:
            return
        rs = list(self._ratios)
        mean_r = sum(rs) / self.lookback
        std_r = math.sqrt(sum((r - mean_r) ** 2 for r in rs) / self.lookback)
        self.value = (rs[-1] - mean_r) / std_r if std_r > 1e-12 else 0.0
        self._set_initialized(True)

    def handle_bar(self, bar: Bar) -> None:
        pass


class GapReturnStd(Indicator):
    """Rolling std of close-to-close returns (Chan buy-on-gap, 90-day)."""

    def __init__(self, period: int) -> None:
        PyCondition.positive_int(period, "period")
        super().__init__(params=[period])
        self.period = period
        self.value: float = 0.0
        self._returns: deque[float] = deque(maxlen=period)
        self._prev_close: float | None = None

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        close = bar.close.as_double()
        if self._prev_close is not None and self._prev_close > 0:
            ret = (close - self._prev_close) / self._prev_close
            self._returns.append(ret)
            self._set_has_inputs(True)
        self._prev_close = close
        if len(self._returns) < self.period:
            return
        rs = list(self._returns)
        mean_r = sum(rs) / self.period
        var_r = sum((r - mean_r) ** 2 for r in rs) / self.period
        self.value = math.sqrt(var_r) if var_r > 0 else 0.0
        self._set_initialized(True)
