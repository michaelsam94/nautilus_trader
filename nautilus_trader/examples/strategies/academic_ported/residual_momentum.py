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

"""Residual momentum vs a benchmark index."""

from collections import deque

from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType

from nautilus_trader.examples.strategies.academic_ported.indicators import RollingBeta
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class ResidualMomentumConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``ResidualMomentum``."""

    benchmark_bar_type: BarType
    lookback_days: PositiveInt = 252
    skip_days: PositiveInt = 21
    beta_period: PositiveInt = 252
    historical_bars_days: PositiveInt = 400


class ResidualMomentum(FreqtradeLongOnlyStrategy):
    """
    Long when beta-adjusted trailing return is positive.

    Single-asset proxy for ``residual-momentum-factor.py``.
    """

    def __init__(self, config: ResidualMomentumConfig) -> None:
        super().__init__(config)
        self._beta = RollingBeta(config.beta_period)
        self._asset_closes: deque[float] = deque(maxlen=config.lookback_days + 1)
        self._bench_closes: deque[float] = deque(maxlen=config.lookback_days + 1)
        self._residual_momentum: float = 0.0
        self._bench_close: float | None = None

    def all_bar_types(self) -> tuple[BarType, ...]:
        return (self.port_config.bar_type, self.config.benchmark_bar_type)

    def all_bar_types(self) -> tuple[BarType, ...]:
        return (self.port_config.bar_type, self.config.benchmark_bar_type)

    def _register_indicators(self) -> None:
        pass

    def indicators_initialized(self) -> bool:
        return self._beta.initialized and len(self._asset_closes) > self.config.lookback_days and len(self._asset_closes) > self.config.lookback_days

    def _update_residual(self) -> None:
        if len(self._asset_closes) <= self.config.lookback_days:
            return
        if len(self._bench_closes) <= self.config.lookback_days:
            return
        if not self._beta.initialized:
            return

        assets = list(self._asset_closes)
        benches = list(self._bench_closes)
        end = len(assets) - self.config.skip_days
        start = end - self.config.lookback_days
        if start < 1 or end <= start:
            return

        asset_ret = assets[end] / assets[start] - 1.0
        bench_ret = benches[end] / benches[start] - 1.0
        self._residual_momentum = asset_ret - self._beta.value * bench_ret

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type == self.config.benchmark_bar_type:
            bench = bar.close.as_double()
            self._bench_closes.append(bench)
            self._bench_close = bench
            self._update_residual()
            return

        if self._bench_close is not None:
            self._beta.update_prices(bar.close.as_double(), self._bench_close)
        self._asset_closes.append(bar.close.as_double())
        self._update_residual()
        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        return self._residual_momentum > 0

    def check_exit(self, bar: Bar) -> bool:
        return self._residual_momentum <= 0
