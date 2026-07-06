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

"""Quarterly relative-strength momentum on one symbol."""

from datetime import date

from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.academic_ported.indicators import LaggedReturn
from nautilus_trader.examples.strategies.academic_ported.indicators import bar_utc_date
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class PairedSwitchingConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``PairedSwitching``."""

    quarter_days: PositiveInt = 63
    historical_bars_days: PositiveInt = 120


class PairedSwitching(FreqtradeLongOnlyStrategy):
    """
    Long when quarterly return is positive; flat otherwise.

    Single-instrument simplification of ``paired-switching.py`` (dual-fund
    rotation in source).
    """

    def __init__(self, config: PairedSwitchingConfig) -> None:
        super().__init__(config)
        self._quarterly = LaggedReturn(config.quarter_days, 0)
        self._prev_date: date | None = None
        self._last_rebalance_month: int | None = None

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._quarterly)

    def check_entry(self, bar: Bar) -> bool:
        return self._quarterly.value > 0

    def check_exit(self, bar: Bar) -> bool:
        return self._quarterly.value <= 0

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        current = bar_utc_date(bar)
        if self._prev_date is not None and current == self._prev_date:
            return
        self._prev_date = current

        if current.month % 3 != 0:
            return
        if self._last_rebalance_month == current.month:
            return
        self._last_rebalance_month = current.month

        iid = self.port_config.instrument_id
        if self.check_exit(bar):
            if self.portfolio.is_net_long(iid):
                self.exit_long()
            return

        if self.check_entry(bar) and self.portfolio.is_flat(iid):
            self.enter_long()
