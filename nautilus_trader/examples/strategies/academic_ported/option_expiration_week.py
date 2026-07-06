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

"""Option-expiration-week calendar effect."""

from datetime import date

from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.academic_ported.indicators import bar_utc_date
from nautilus_trader.examples.strategies.academic_ported.indicators import is_option_expiration_week
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class OptionExpirationWeekConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``OptionExpirationWeek``."""


class OptionExpirationWeek(FreqtradeLongOnlyStrategy):
    """
    Long during the week containing the third Friday; flat otherwise.

    Calendar proxy for ``option-expiration-week-effect.py``.
    """

    def __init__(self, config: OptionExpirationWeekConfig) -> None:
        super().__init__(config)
        self._prev_date: date | None = None
        self._in_week = False

    def _register_indicators(self) -> None:
        pass

    def indicators_initialized(self) -> bool:
        return True

    def check_entry(self, bar: Bar) -> bool:
        return self._in_week

    def check_exit(self, bar: Bar) -> bool:
        return not self._in_week

    def on_bar(self, bar: Bar) -> None:
        if bar.is_single_price():
            return

        current = bar_utc_date(bar)
        if self._prev_date is not None and current == self._prev_date:
            return
        self._prev_date = current
        self._in_week = is_option_expiration_week(current)

        iid = self.port_config.instrument_id
        if not self._in_week and self.portfolio.is_net_long(iid):
            self.exit_long()
            return
        if self._in_week and self.portfolio.is_flat(iid):
            self.enter_long()
