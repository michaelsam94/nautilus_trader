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

"""Low-beta long filter vs a benchmark index."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType

from nautilus_trader.examples.strategies.academic_ported.indicators import RollingBeta
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class LowBetaConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``LowBeta``."""

    benchmark_bar_type: BarType
    beta_period: PositiveInt = 252
    max_beta: PositiveFloat = 0.8
    historical_bars_days: PositiveInt = 400


class LowBeta(FreqtradeLongOnlyStrategy):
    """
    Long when rolling beta vs benchmark is below a threshold.

    Single-asset simplification of ``betting-against-beta-factor-in-stocks.py``
    and ``betting-against-beta-factor-in-country-equity-indexes.py``.
    """

    def __init__(self, config: LowBetaConfig) -> None:
        super().__init__(config)
        self._beta = RollingBeta(config.beta_period)
        self._bench_close: float | None = None

    def all_bar_types(self) -> tuple[BarType, ...]:
        return (self.port_config.bar_type, self.config.benchmark_bar_type)

    def _register_indicators(self) -> None:
        pass

    def indicators_initialized(self) -> bool:
        return self._beta.initialized

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type == self.config.benchmark_bar_type:
            self._bench_close = bar.close.as_double()
            return

        if self._bench_close is not None:
            self._beta.update_prices(bar.close.as_double(), self._bench_close)
        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        if not self._beta.initialized:
            return False
        return self._beta.value < self.config.max_beta

    def check_exit(self, bar: Bar) -> bool:
        if not self._beta.initialized:
            return False
        return self._beta.value >= self.config.max_beta
