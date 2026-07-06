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

"""Turn-of-the-month calendar effect."""

from datetime import date

from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.academic_ported.indicators import bar_utc_date
from nautilus_trader.examples.strategies.academic_ported.indicators import is_month_end_bar
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class TurnOfTheMonthConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``TurnOfTheMonth``."""

    hold_days: int = 3


class TurnOfTheMonth(FreqtradeLongOnlyStrategy):
    """
    Enter at month-end; exit on the Nth trading day of the new month.

    Port of ``turn-of-the-month-in-equity-indexes.py``.
    """

    def __init__(self, config: TurnOfTheMonthConfig) -> None:
        super().__init__(config)
        self._prev_date: date | None = None
        self._days_in_month: int = 0

    def check_entry(self, bar: Bar) -> bool:
        return is_month_end_bar(bar)

    def check_exit(self, bar: Bar) -> bool:
        return False

    def on_bar(self, bar: Bar) -> None:
        if bar.is_single_price():
            return

        current = bar_utc_date(bar)
        if self._prev_date is not None and current.month != self._prev_date.month:
            self._days_in_month = 1
        elif self._prev_date is not None and current == self._prev_date:
            pass
        else:
            self._days_in_month += 1
        self._prev_date = current

        iid = self.port_config.instrument_id
        if self._days_in_month >= self.config.hold_days and self.portfolio.is_net_long(iid):
            self.exit_long()
            return

        if self.check_entry(bar) and self.portfolio.is_flat(iid):
            self.enter_long()
