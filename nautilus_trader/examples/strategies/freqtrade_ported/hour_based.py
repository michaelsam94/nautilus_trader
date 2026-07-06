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

"""Port of Freqtrade ``HourBasedStrategy`` (time-of-day entries/exits)."""

from datetime import datetime
from datetime import timezone

from nautilus_trader.config import NonNegativeInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import hour_in_range


class HourBasedConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``HourBased`` (ported from Freqtrade)."""

    buy_hour_min: NonNegativeInt = 4
    buy_hour_max: NonNegativeInt = 24
    sell_hour_min: NonNegativeInt = 22
    sell_hour_max: NonNegativeInt = 21


class HourBased(FreqtradeLongOnlyStrategy):
    """
    Enter during configured buy hours; exit during sell hours.

    Ported from ``user_data/strategies/HourBasedStrategy.py``.
    Intended for 1h bars (UTC hour).
    """

    @staticmethod
    def _bar_hour(bar: Bar) -> int:
        return datetime.fromtimestamp(bar.ts_event / 1e9, tz=timezone.utc).hour

    def check_entry(self, bar: Bar) -> bool:
        hour = self._bar_hour(bar)
        cfg = self.config
        return hour_in_range(hour, cfg.buy_hour_min, cfg.buy_hour_max)

    def check_exit(self, bar: Bar) -> bool:
        hour = self._bar_hour(bar)
        cfg = self.config
        return hour_in_range(hour, cfg.sell_hour_min, cfg.sell_hour_max)
