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

"""Chan Example 4.1: intraday buy-on-gap mean reversion."""

from datetime import datetime
from datetime import timezone

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.chan_ported.indicators import GapReturnStd
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class BuyOnGapConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``BuyOnGap``."""

    entry_z: PositiveFloat = 1.0
    return_std_period: PositiveInt = 90
    session_open_hour: PositiveInt = 14
    session_close_hour: PositiveInt = 20
    historical_bars_days: PositiveInt = 120


class BuyOnGap(FreqtradeLongOnlyStrategy):
    """
    Buy when open gaps below prior low minus z * rolling return volatility.

    Chan (2013) Example 4.1, Ch.4 p.110. Single-instrument proxy for SPX
    universe scan; multi-stock top-N selection requires universe data.
    """

    def __init__(self, config: BuyOnGapConfig) -> None:
        super().__init__(config)
        self._ret_std = GapReturnStd(config.return_std_period)
        self._prev_low: float | None = None
        self._prev_close: float | None = None
        self._entered_today: bool = False
        self._current_day: int | None = None

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._ret_std)

    @staticmethod
    def _bar_dt(bar: Bar) -> datetime:
        return datetime.fromtimestamp(bar.ts_event / 1e9, tz=timezone.utc)

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type != self.port_config.bar_type:
            return
        if bar.is_single_price():
            return

        dt = self._bar_dt(bar)
        day = dt.date().toordinal()
        if self._current_day != day:
            self._current_day = day
            self._entered_today = False

        low = bar.low.as_double()
        close = bar.close.as_double()
        open_px = bar.open.as_double()
        cfg = self.config

        if self.portfolio.is_net_long(self.port_config.instrument_id):
            if dt.hour >= cfg.session_close_hour or self.check_exit(bar):
                self.exit_long()
            return

        if (
            not self._entered_today
            and self._ret_std.initialized
            and self._prev_low is not None
            and dt.hour == cfg.session_open_hour
        ):
            buy_level = self._prev_low * (1.0 - cfg.entry_z * self._ret_std.value)
            gap_ret = (open_px - self._prev_low) / self._prev_low if self._prev_low > 0 else 0.0
            if open_px <= buy_level and gap_ret < 0 and self.portfolio.is_flat(
                self.port_config.instrument_id,
            ):
                self.enter_long()
                self._entered_today = True

        self._prev_low = low
        self._prev_close = close

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        if self._prev_close is None:
            return False
        return bar.close.as_double() >= self._prev_close
