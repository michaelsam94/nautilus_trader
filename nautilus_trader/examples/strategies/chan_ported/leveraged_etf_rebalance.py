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

"""Chan Ch.7: constant-leverage leveraged ETF rebalance strategy."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class LeveragedEtfRebalanceConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``LeveragedEtfRebalance``."""

    target_leverage: PositiveFloat = 3.0
    rebalance_threshold: PositiveFloat = 0.05


class LeveragedEtfRebalance(FreqtradeLongOnlyStrategy):
    """
    Maintain target leverage by scaling position at each bar close.

    Chan (2013) Ch.7 p.181 leveraged ETF / constant leverage portfolio.
    Single-instrument proxy; full RMZ 3x requires index composition data.
    """

    def __init__(self, config: LeveragedEtfRebalanceConfig) -> None:
        super().__init__(config)
        self._entry_price: float | None = None

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type != self.port_config.bar_type or bar.is_single_price():
            return
        if not self.indicators_initialized():
            return

        close = bar.close.as_double()
        iid = self.port_config.instrument_id
        position = self.portfolio.position(iid)

        if position is None or position.is_flat:
            if self.check_entry(bar):
                self.enter_long()
                self._entry_price = close
            return

        if self._entry_price is None or self._entry_price <= 0:
            self._entry_price = position.avg_px_open.as_double()
            return

        current_leverage = close / self._entry_price
        target = self.config.target_leverage
        drift = abs(current_leverage - target) / target
        if drift > self.config.rebalance_threshold:
            self.exit_long()
            self.enter_long()
            self._entry_price = close

    def check_entry(self, bar: Bar) -> bool:
        return True

    def check_exit(self, bar: Bar) -> bool:
        return False
