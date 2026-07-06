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

"""Port of jesse-ai/example-strategies ``Donchian`` (SMA200 trend filter)."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import DonchianChannel
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class DonchianSma200Config(FreqtradePortConfig, frozen=True):
    """Configuration for ``DonchianSma200``."""

    donchian_period: PositiveInt = 20
    trend_sma_period: PositiveInt = 200
    historical_bars_days: PositiveInt = 250


class DonchianSma200(FreqtradeLongOnlyStrategy):
    """
    Donchian upper-band breakout with SMA200 uptrend filter.

    Ported from jesse-ai/example-strategies ``Donchian``.
    Uses prior-bar Donchian bands (excludes current bar), matching Jesse semantics.
    """

    def __init__(self, config: DonchianSma200Config) -> None:
        super().__init__(config)
        self._donchian = DonchianChannel(config.donchian_period)
        self._sma = SimpleMovingAverage(config.trend_sma_period)
        self._prev_upper: float | None = None
        self._prev_lower: float | None = None

    def _register_indicators(self) -> None:
        bt = self.port_config.bar_type
        self.register_indicator_for_bars(bt, self._donchian)
        self.register_indicator_for_bars(bt, self._sma)

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        close = bar.close.as_double()
        upper = self._donchian.upper
        lower = self._donchian.lower

        iid = self.port_config.instrument_id
        if self._prev_lower is not None and self.portfolio.is_net_long(iid):
            if close < self._prev_lower:
                self.exit_long()
                self._prev_upper = upper
                self._prev_lower = lower
                return

        if (
            self._prev_upper is not None
            and close > self._sma.value
            and close > self._prev_upper
            and self.portfolio.is_flat(iid)
        ):
            self.enter_long()

        self._prev_upper = upper
        self._prev_lower = lower

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        return False
