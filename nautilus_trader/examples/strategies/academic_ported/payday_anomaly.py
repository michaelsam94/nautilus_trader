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

"""Payday (mid-month) calendar anomaly."""

from datetime import date

from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.academic_ported.indicators import bar_utc_date
from nautilus_trader.examples.strategies.academic_ported.indicators import payday_for_month
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class PaydayAnomalyConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``PaydayAnomaly``."""


class PaydayAnomaly(FreqtradeLongOnlyStrategy):
    """
    Enter on the mid-month payday; exit on the next bar.

    Port of ``payday-anomaly.py``.
    """

    def __init__(self, config: PaydayAnomalyConfig) -> None:
        super().__init__(config)
        self._exit_next_bar = False
        self._prev_date: date | None = None

    def check_entry(self, bar: Bar) -> bool:
        d = bar_utc_date(bar)
        return d == payday_for_month(d.year, d.month)

    def check_exit(self, bar: Bar) -> bool:
        return self._exit_next_bar

    def on_bar(self, bar: Bar) -> None:
        if bar.is_single_price():
            return

        current = bar_utc_date(bar)
        if self._prev_date is not None and current == self._prev_date:
            return
        self._prev_date = current

        iid = self.port_config.instrument_id
        if self.check_exit(bar):
            self._exit_next_bar = False
            if self.portfolio.is_net_long(iid):
                self.exit_long()
            return

        if self.check_entry(bar) and self.portfolio.is_flat(iid):
            self.enter_long()
            self._exit_next_bar = True
