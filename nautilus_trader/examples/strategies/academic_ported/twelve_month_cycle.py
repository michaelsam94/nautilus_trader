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

"""Seasonal 12-month-lagged monthly return signal."""

from datetime import date

from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.academic_ported.indicators import LaggedReturn
from nautilus_trader.examples.strategies.academic_ported.indicators import bar_utc_date
from nautilus_trader.examples.strategies.academic_ported.indicators import is_month_end_bar
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class TwelveMonthCycleConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``TwelveMonthCycle``."""

    year_lag_days: PositiveInt = 252
    month_window_days: PositiveInt = 21
    historical_bars_days: PositiveInt = 400


class TwelveMonthCycle(FreqtradeLongOnlyStrategy):
    """
    Hold through the month when the same-month return one year ago was positive.

    Simplified port of ``12-month-cycle-in-cross-section-of-stocks-returns.py``.
    """

    def __init__(self, config: TwelveMonthCycleConfig) -> None:
        super().__init__(config)
        end_lag = config.year_lag_days - config.month_window_days
        start_lag = config.year_lag_days
        self._seasonal = LaggedReturn(start_lag, end_lag)
        self._hold_next_month = False
        self._prev_date: date | None = None

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._seasonal)

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        return False

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        current = bar_utc_date(bar)
        is_new_month = (
            self._prev_date is not None and current.month != self._prev_date.month
        )
        self._prev_date = current

        if is_month_end_bar(bar):
            self._hold_next_month = self._seasonal.value > 0

        iid = self.port_config.instrument_id
        if is_new_month:
            if self._hold_next_month and self.portfolio.is_flat(iid):
                self.enter_long()
            elif not self._hold_next_month and self.portfolio.is_net_long(iid):
                self.exit_long()
