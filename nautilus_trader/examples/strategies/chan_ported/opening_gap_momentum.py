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

"""Chan Example 7.1: opening gap momentum strategy."""

from datetime import datetime
from datetime import timezone

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.chan_ported.indicators import GapReturnStd
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class OpeningGapMomentumConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``OpeningGapMomentum``."""

    entry_z: PositiveFloat = 0.1
    return_std_period: PositiveInt = 90
    session_open_hour: PositiveInt = 14
    session_close_hour: PositiveInt = 20
    historical_bars_days: PositiveInt = 120


class OpeningGapMomentum(FreqtradeLongOnlyStrategy):
    """
    Long when open gaps up beyond z * prior close-to-close return volatility.

    Chan (2013) Example 7.1, Ch.7 p.174 (FSTX futures gap momentum).
    """

    def __init__(self, config: OpeningGapMomentumConfig) -> None:
        super().__init__(config)
        self._ret_std = GapReturnStd(config.return_std_period)
        self._prev_close: float | None = None
        self._entered_today: bool = False
        self._current_day: int | None = None

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._ret_std)

    @staticmethod
    def _bar_dt(bar: Bar) -> datetime:
        return datetime.fromtimestamp(bar.ts_event / 1e9, tz=timezone.utc)

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type != self.port_config.bar_type or bar.is_single_price():
            return

        dt = self._bar_dt(bar)
        day = dt.date().toordinal()
        if self._current_day != day:
            self._current_day = day
            self._entered_today = False

        open_px = bar.open.as_double()
        close = bar.close.as_double()
        cfg = self.config

        if self.portfolio.is_net_long(self.port_config.instrument_id):
            if dt.hour >= cfg.session_close_hour:
                self.exit_long()
            return

        if (
            not self._entered_today
            and self._ret_std.initialized
            and self._prev_close is not None
            and self._prev_close > 0
            and dt.hour == cfg.session_open_hour
        ):
            threshold = self._prev_close * (1.0 + cfg.entry_z * self._ret_std.value)
            if open_px > threshold and self.portfolio.is_flat(self.port_config.instrument_id):
                self.enter_long()
                self._entered_today = True

        self._prev_close = close

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        return False
