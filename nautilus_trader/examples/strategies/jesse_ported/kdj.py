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

"""Port of jesse-ai/example-strategies ``KDJ`` (long only)."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import ShiftedValue
from nautilus_trader.examples.strategies.jesse_ported.indicators import KDJ


class KdjConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``Kdj``."""

    fastk_period: PositiveInt = 9
    slowk_period: PositiveInt = 3
    slowd_period: PositiveInt = 3
    historical_bars_days: PositiveInt = 60


class Kdj(FreqtradeLongOnlyStrategy):
    """
    Enter when J > K and J > D; exit when J falls below both or J declines in profit.

    Ported from jesse-ai/example-strategies ``KDJstrategy``.
    ATR stop-loss from Jesse source omitted.
    """

    def __init__(self, config: KdjConfig) -> None:
        super().__init__(config)
        self._kdj = KDJ(config.fastk_period, config.slowk_period, config.slowd_period)
        self._prev_j = ShiftedValue()
        self._entry_price: float | None = None

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._kdj)

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        prev_j = self._prev_j.update(self._kdj.j)
        close = bar.close.as_double()
        iid = self.port_config.instrument_id
        j_above = self._kdj.j > self._kdj.k and self._kdj.j > self._kdj.d
        j_below = self._kdj.j < self._kdj.k and self._kdj.j < self._kdj.d

        if self.portfolio.is_net_long(iid):
            in_profit = self._entry_price is not None and close > self._entry_price
            if in_profit and prev_j is not None and prev_j > self._kdj.j:
                self.exit_long()
                self._entry_price = None
            elif j_below:
                self.exit_long()
                self._entry_price = None
        elif j_above:
            self.enter_long()
            self._entry_price = close

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        return False
