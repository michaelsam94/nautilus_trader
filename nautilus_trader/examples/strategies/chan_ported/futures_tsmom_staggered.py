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

"""Chan Example 6.1: time-series momentum with staggered holding period."""

from collections import deque

from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import RateOfChange
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class FuturesTsmomStaggeredConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``FuturesTsmomStaggered``."""

    lookback: PositiveInt = 250
    hold_days: PositiveInt = 25
    historical_bars_days: PositiveInt = 400


class FuturesTsmomStaggered(FreqtradeLongOnlyStrategy):
    """
    Long when price exceeds lookback-ago level; hold for ``hold_days`` bars.

    Chan (2013) Example 6.1, Ch.6 p.155 (TU futures). Distinct from
    ``academic_ported.time_series_momentum`` which uses ROC sign without
    explicit staggered hold-day overlay.
    """

    def __init__(self, config: FuturesTsmomStaggeredConfig) -> None:
        super().__init__(config)
        self._roc = RateOfChange(config.lookback)
        self._closes: deque[float] = deque(maxlen=config.lookback + 1)
        self._bars_in_trade: int = 0

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._roc)

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type != self.port_config.bar_type:
            return
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        close = bar.close.as_double()
        self._closes.append(close)
        iid = self.port_config.instrument_id

        if self.portfolio.is_net_long(iid):
            self._bars_in_trade += 1
            if self._bars_in_trade >= self.config.hold_days or self.check_exit(bar):
                self.exit_long()
                self._bars_in_trade = 0
            return

        if self.portfolio.is_flat(iid) and self.check_entry(bar):
            self.enter_long()
            self._bars_in_trade = 0

    def check_entry(self, bar: Bar) -> bool:
        if len(self._closes) < self.config.lookback + 1:
            return False
        closes = list(self._closes)
        return closes[-1] > closes[0]

    def check_exit(self, bar: Bar) -> bool:
        if len(self._closes) < self.config.lookback + 1:
            return True
        closes = list(self._closes)
        return closes[-1] < closes[0]
