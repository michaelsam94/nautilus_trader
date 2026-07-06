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

"""Port of je-suis-tm/quant-trading London Breakout."""

from datetime import datetime
from datetime import timezone

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class LondonBreakoutConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``LondonBreakout``."""

    pre_session_hour: PositiveInt = 2
    session_open_hour: PositiveInt = 3
    session_open_minutes: PositiveInt = 30
    session_close_hour: PositiveInt = 12
    risky_stop: PositiveFloat = 0.01
    profit_stop_fraction: PositiveFloat = 0.5


class LondonBreakout(FreqtradeLongOnlyStrategy):
    """
    Tokyo-range breakout at London open (long only).

    Source: je-suis-tm/quant-trading ``London Breakout backtest.py``.
    """

    def __init__(self, config: LondonBreakoutConfig) -> None:
        super().__init__(config)
        self._tokyo_prices: list[float] = []
        self._upper: float = 0.0
        self._lower: float = 0.0
        self._executed_price: float = 0.0
        self._entered_today: bool = False
        self._current_day: int | None = None

    @staticmethod
    def _bar_dt(bar: Bar) -> datetime:
        return datetime.fromtimestamp(bar.ts_event / 1e9, tz=timezone.utc)

    def on_bar(self, bar: Bar) -> None:
        if bar.is_single_price():
            return

        dt = self._bar_dt(bar)
        day = dt.date().toordinal()
        if self._current_day != day:
            self._current_day = day
            self._tokyo_prices.clear()
            self._entered_today = False
            self._executed_price = 0.0

        close = bar.close.as_double()
        cfg = self.config

        if dt.hour == cfg.pre_session_hour:
            self._tokyo_prices.append(close)

        if dt.hour == cfg.session_open_hour and dt.minute == 0 and self._tokyo_prices:
            self._upper = max(self._tokyo_prices)
            self._lower = min(self._tokyo_prices)
            self._tokyo_prices.clear()

        if (
            dt.hour == cfg.session_open_hour
            and dt.minute < cfg.session_open_minutes
            and self._upper > 0
            and not self._entered_today
        ):
            if close > self._upper and (close - self._upper) <= cfg.risky_stop:
                if self.portfolio.is_flat(self.port_config.instrument_id):
                    self.enter_long()
                self._executed_price = close
                self._entered_today = True

        if self.portfolio.is_net_long(self.port_config.instrument_id) and self._executed_price > 0:
            target = self._executed_price * (1.0 + cfg.risky_stop * cfg.profit_stop_fraction)
            stop = self._executed_price * (1.0 - cfg.risky_stop * cfg.profit_stop_fraction)
            if close >= target or close <= stop:
                self.exit_long()
                self._executed_price = 0.0

        if dt.hour == cfg.session_close_hour and self.portfolio.is_net_long(
            self.port_config.instrument_id,
        ):
            self.exit_long()

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        return False
