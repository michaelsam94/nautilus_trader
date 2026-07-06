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

"""Oil-return regression signal for equity exposure."""

from collections import deque
from datetime import date

from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType

from nautilus_trader.examples.strategies.academic_ported.indicators import bar_utc_date
from nautilus_trader.examples.strategies.academic_ported.indicators import is_month_end_bar
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class CrudeOilEquityConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``CrudeOilEquity``."""

    oil_bar_type: BarType
    min_months: PositiveInt = 13
    historical_bars_days: PositiveInt = 500


class CrudeOilEquity(FreqtradeLongOnlyStrategy):
    """
    Long equity when oil-predicted market return is positive.

    Simplified port of ``crude-oil-predicts-equity-returns.py`` using monthly
    returns and a rolling linear regression (risk-free threshold omitted).
    """

    def __init__(self, config: CrudeOilEquityConfig) -> None:
        super().__init__(config)
        self._equity_monthly: deque[float] = deque(maxlen=60)
        self._oil_monthly: deque[float] = deque(maxlen=60)
        self._last_equity_month: float | None = None
        self._last_oil_month: float | None = None
        self._expected_return: float = 0.0
        self._oil_close: float | None = None
        self._prev_date: date | None = None

    def all_bar_types(self) -> tuple[BarType, ...]:
        return (self.port_config.bar_type, self.config.oil_bar_type)

    def _register_indicators(self) -> None:
        pass

    def indicators_initialized(self) -> bool:
        return len(self._equity_monthly) >= self.config.min_months

    def _linregress(self, x: list[float], y: list[float]) -> tuple[float, float]:
        n = len(x)
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        var_x = sum((xi - mean_x) ** 2 for xi in x)
        if var_x < 1e-12:
            return 0.0, mean_y
        cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        slope = cov / var_x if var_x != 0 else 0.0
        intercept = mean_y - slope * mean_x
        return slope, intercept

    def _recompute_signal(self) -> None:
        if len(self._equity_monthly) < self.config.min_months:
            return
        if len(self._oil_monthly) < self.config.min_months:
            return

        equities = list(self._equity_monthly)
        oils = list(self._oil_monthly)
        n = min(len(equities), len(oils))
        equities = equities[-n:]
        oils = oils[-n:]

        market_rets = [
            (equities[i] - equities[i - 1]) / equities[i - 1]
            for i in range(1, n)
            if equities[i - 1] != 0
        ]
        oil_rets = [
            (oils[i] - oils[i - 1]) / oils[i - 1]
            for i in range(1, n)
            if oils[i - 1] != 0
        ]
        m = min(len(market_rets), len(oil_rets))
        if m < 2:
            return

        market_rets = market_rets[-m:]
        oil_rets = oil_rets[-m:]
        slope, intercept = self._linregress(oil_rets[:-1], market_rets[1:])
        self._expected_return = intercept + slope * oil_rets[-1]

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type == self.config.oil_bar_type:
            self._oil_close = bar.close.as_double()
            return

        current = bar_utc_date(bar)
        if self._prev_date is not None and current == self._prev_date:
            return
        self._prev_date = current

        if is_month_end_bar(bar):
            close = bar.close.as_double()
            self._equity_monthly.append(close)
            if self._oil_close is not None:
                self._oil_monthly.append(self._oil_close)
            self._recompute_signal()

        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        return self._expected_return > 0

    def check_exit(self, bar: Bar) -> bool:
        return self._expected_return <= 0
