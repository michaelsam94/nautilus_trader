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

"""Indicators and calendar helpers for academic strategy ports."""

from __future__ import annotations

import math
from collections import deque
from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone

from nautilus_trader.core.correctness import PyCondition
from nautilus_trader.indicators import Indicator
from nautilus_trader.model.data import Bar


def bar_utc_date(bar: Bar) -> date:
    """UTC calendar date for a bar event."""
    return datetime.fromtimestamp(bar.ts_event / 1e9, tz=timezone.utc).date()


def is_month_end_bar(bar: Bar) -> bool:
    """True when the bar falls on the last calendar day of its month."""
    d = bar_utc_date(bar)
    return (d + timedelta(days=1)).month != d.month


def third_friday(year: int, month: int) -> date:
    """Third Friday of a calendar month (US equity options expiration)."""
    fridays: list[int] = []
    d = date(year, month, 1)
    while d.month == month:
        if d.weekday() == 4:
            fridays.append(d.day)
        d += timedelta(days=1)
    return date(year, month, fridays[2])


def is_option_expiration_week(d: date) -> bool:
    """True during the Monday–Friday week containing the third Friday."""
    opex = third_friday(d.year, d.month)
    week_start = opex - timedelta(days=opex.weekday())
    week_end = week_start + timedelta(days=4)
    return week_start <= d <= week_end


def payday_for_month(year: int, month: int) -> date:
    """15th of month, shifted to Friday when the 15th is on a weekend."""
    payday = date(year, month, 15)
    if payday.weekday() == 5:
        return payday - timedelta(days=1)
    if payday.weekday() == 6:
        return payday - timedelta(days=2)
    return payday


class RollingMaximum(Indicator):
    """Rolling maximum of bar closes."""

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
        self.value = max(self._closes)
        self._set_has_inputs(True)
        if len(self._closes) == self.period:
            self._set_initialized(True)

    def _reset(self) -> None:
        self.value = 0.0
        self._closes.clear()


class LaggedReturn(Indicator):
    """Return between close ``end_lag`` bars ago and ``start_lag`` bars ago."""

    def __init__(self, start_lag: int, end_lag: int) -> None:
        PyCondition.positive_int(start_lag, "start_lag")
        PyCondition.positive_int(end_lag, "end_lag")
        PyCondition.is_true(start_lag > end_lag, "start_lag must exceed end_lag")
        super().__init__(params=[start_lag, end_lag])
        self.start_lag = start_lag
        self.end_lag = end_lag
        self.value: float = 0.0
        self._closes: deque[float] = deque(maxlen=start_lag + 1)

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        self._closes.append(bar.close.as_double())
        self._set_has_inputs(True)
        if len(self._closes) > self.start_lag:
            recent = self._closes[-(self.end_lag + 1)]
            older = self._closes[-(self.start_lag + 1)]
            self.value = recent / older - 1.0 if older != 0 else 0.0
            self._set_initialized(True)

    def _reset(self) -> None:
        self.value = 0.0
        self._closes.clear()


class RealizedVolatility(Indicator):
    """Annualized standard deviation of daily log returns."""

    def __init__(self, period: int) -> None:
        PyCondition.positive_int(period, "period")
        super().__init__(params=[period])
        self.period = period
        self.value: float = 0.0
        self._closes: deque[float] = deque(maxlen=period + 1)

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        self._closes.append(bar.close.as_double())
        self._set_has_inputs(True)
        if len(self._closes) < 2:
            return

        rets: list[float] = []
        closes = list(self._closes)
        for i in range(1, len(closes)):
            if closes[i - 1] != 0:
                rets.append(math.log(closes[i] / closes[i - 1]))

        if len(rets) < self.period:
            return

        sample = rets[-self.period :]
        mean = sum(sample) / len(sample)
        var = sum((x - mean) ** 2 for x in sample) / len(sample)
        self.value = math.sqrt(var) * math.sqrt(252.0)
        self._set_initialized(True)

    def _reset(self) -> None:
        self.value = 0.0
        self._closes.clear()


class ReturnSkewness(Indicator):
    """Rolling sample skewness of simple daily returns."""

    def __init__(self, period: int) -> None:
        PyCondition.positive_int(period, "period")
        super().__init__(params=[period])
        self.period = period
        self.value: float = 0.0
        self._closes: deque[float] = deque(maxlen=period + 1)

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        self._closes.append(bar.close.as_double())
        self._set_has_inputs(True)
        if len(self._closes) < 2:
            return

        rets: list[float] = []
        closes = list(self._closes)
        for i in range(1, len(closes)):
            if closes[i - 1] != 0:
                rets.append(closes[i] / closes[i - 1] - 1.0)

        if len(rets) < self.period:
            return

        sample = rets[-self.period :]
        n = len(sample)
        mean = sum(sample) / n
        std = math.sqrt(sum((x - mean) ** 2 for x in sample) / n)
        if std < 1e-12:
            self.value = 0.0
        else:
            self.value = sum(((x - mean) / std) ** 3 for x in sample) / n
        self._set_initialized(True)

    def _reset(self) -> None:
        self.value = 0.0
        self._closes.clear()


class RollingBeta(Indicator):
    """Rolling OLS beta of asset returns vs benchmark returns."""

    def __init__(self, period: int) -> None:
        PyCondition.positive_int(period, "period")
        super().__init__(params=[period])
        self.period = period
        self.value: float = 1.0
        self._asset_closes: deque[float] = deque(maxlen=period + 1)
        self._bench_closes: deque[float] = deque(maxlen=period + 1)

    def update_prices(self, asset_close: float, bench_close: float) -> None:
        self._asset_closes.append(asset_close)
        self._bench_closes.append(bench_close)
        self._set_has_inputs(True)
        if len(self._asset_closes) < 2 or len(self._bench_closes) < 2:
            return

        asset_rets: list[float] = []
        bench_rets: list[float] = []
        assets = list(self._asset_closes)
        benches = list(self._bench_closes)
        for i in range(1, len(assets)):
            if assets[i - 1] != 0 and benches[i - 1] != 0:
                asset_rets.append(assets[i] / assets[i - 1] - 1.0)
                bench_rets.append(benches[i] / benches[i - 1] - 1.0)

        if len(asset_rets) < self.period:
            return

        a = asset_rets[-self.period :]
        b = bench_rets[-self.period :]
        mean_b = sum(b) / len(b)
        var_b = sum((x - mean_b) ** 2 for x in b) / len(b)
        if var_b < 1e-12:
            return
        mean_a = sum(a) / len(a)
        cov = sum((a[i] - mean_a) * (b[i] - mean_b) for i in range(len(a))) / len(a)
        self.value = cov / var_b
        self._set_initialized(True)

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        self.update_prices(bar.close.as_double(), bar.close.as_double())

    def _reset(self) -> None:
        self.value = 1.0
        self._asset_closes.clear()
        self._bench_closes.clear()


class ReturnAsymmetryIndex(Indicator):
    """
    IE asymmetry: count(up-tail days) - count(down-tail days) over a window.

    Tail days exceed mean +/- two standard deviations of daily returns.
    """

    def __init__(self, period: int) -> None:
        PyCondition.positive_int(period, "period")
        super().__init__(params=[period])
        self.period = period
        self.value: float = 0.0
        self._closes: deque[float] = deque(maxlen=period + 1)

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        self._closes.append(bar.close.as_double())
        self._set_has_inputs(True)
        if len(self._closes) < 2:
            return

        rets: list[float] = []
        closes = list(self._closes)
        for i in range(1, len(closes)):
            if closes[i - 1] != 0:
                rets.append(closes[i] / closes[i - 1] - 1.0)

        if len(rets) < self.period:
            return

        sample = rets[-self.period :]
        mean = sum(sample) / len(sample)
        std = math.sqrt(sum((x - mean) ** 2 for x in sample) / len(sample))
        upper = mean + 2.0 * std
        lower = mean - 2.0 * std
        self.value = float(
            sum(1 for x in sample if x > upper) - sum(1 for x in sample if x < lower),
        )
        self._set_initialized(True)

    def _reset(self) -> None:
        self.value = 0.0
        self._closes.clear()
