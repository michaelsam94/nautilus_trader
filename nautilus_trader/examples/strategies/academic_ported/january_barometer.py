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

"""January return barometer on a single equity."""

from datetime import date

from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.academic_ported.indicators import bar_utc_date
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class JanuaryBarometerConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``JanuaryBarometer``."""


class JanuaryBarometer(FreqtradeLongOnlyStrategy):
    """
    Enter in January; remain long after February only if January was positive.

    Simplified port of ``january-barometer.py`` (T-Bill switch omitted).
    """

    def __init__(self, config: JanuaryBarometerConfig) -> None:
        super().__init__(config)
        self._january_start_price: float | None = None
        self._stay_long_year: bool = False
        self._prev_date: date | None = None
        self._last_month: int | None = None

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        return False

    def on_bar(self, bar: Bar) -> None:
        if bar.is_single_price():
            return

        current = bar_utc_date(bar)
        if self._prev_date is not None and current == self._prev_date:
            return
        self._prev_date = current

        month = current.month
        if month == self._last_month:
            return
        self._last_month = month

        iid = self.port_config.instrument_id
        price = bar.close.as_double()

        if month == 1:
            self._january_start_price = price
            self._stay_long_year = False
            if self.portfolio.is_flat(iid):
                self.enter_long()
            return

        if month == 2 and self._january_start_price is not None:
            jan_return = (price - self._january_start_price) / self._january_start_price
            self._stay_long_year = jan_return > 0
            if not self._stay_long_year and self.portfolio.is_net_long(iid):
                self.exit_long()
            return

        if month > 2 and not self._stay_long_year and self.portfolio.is_net_long(iid):
            self.exit_long()
