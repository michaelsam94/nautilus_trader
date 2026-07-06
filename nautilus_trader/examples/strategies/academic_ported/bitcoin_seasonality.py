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

"""Intraday BTC seasonality (22:00–00:00 UTC hold)."""

from datetime import datetime
from datetime import timezone

from nautilus_trader.config import NonNegativeInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class BitcoinSeasonalityConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``BitcoinSeasonality``."""

    open_utc_hour: NonNegativeInt = 22
    close_utc_hour: NonNegativeInt = 0


class BitcoinSeasonality(FreqtradeLongOnlyStrategy):
    """
    Enter long at ``open_utc_hour`` UTC; exit at ``close_utc_hour`` UTC.

    Port of ``intraday-seasonality-in-bitcoin.py``.
    """

    def __init__(self, config: BitcoinSeasonalityConfig) -> None:
        super().__init__(config)
        self._opened_today = False

    def _register_indicators(self) -> None:
        pass

    def indicators_initialized(self) -> bool:
        return True

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        return False

    def on_bar(self, bar: Bar) -> None:
        if bar.is_single_price():
            return

        ts = datetime.fromtimestamp(bar.ts_event / 1e9, tz=timezone.utc)
        iid = self.port_config.instrument_id

        if ts.hour == self.config.open_utc_hour and ts.minute == 0:
            if self.portfolio.is_flat(iid):
                self.enter_long()
            self._opened_today = True
            return

        if ts.hour == self.config.close_utc_hour and ts.minute == 0 and self._opened_today:
            if self.portfolio.is_net_long(iid):
                self.exit_long()
            self._opened_today = False
