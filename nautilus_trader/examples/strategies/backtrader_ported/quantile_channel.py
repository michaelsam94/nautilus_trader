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

"""Port of ali-azary ``QuantileChannelStrategy`` (long only)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.backtrader_ported.indicators import QuantileChannel
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import ShiftedValue


class QuantileChannelBreakoutConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``QuantileChannelBreakout``."""

    lookback_period: PositiveInt = 30
    upper_quantile: PositiveFloat = 0.8
    lower_quantile: PositiveFloat = 0.2
    breakout_threshold: PositiveFloat = 1.01
    rebalance_period: PositiveInt = 7
    min_confidence: PositiveFloat = 0.3
    historical_bars_days: PositiveInt = 60


class QuantileChannelBreakout(FreqtradeLongOnlyStrategy):
    """
    Upper quantile channel breakout entry; exit on return to trend (long only).

    Ported from ali-azary ``QuantileChannelStrategy``; scipy optimizer replaced
    by rolling quantile-regression bands in ``QuantileChannel``.
    """

    def __init__(self, config: QuantileChannelBreakoutConfig) -> None:
        super().__init__(config)
        self._channel = QuantileChannel(
            config.lookback_period,
            config.upper_quantile,
            config.lower_quantile,
        )
        self._prev_close = ShiftedValue()
        self._prev_upper = ShiftedValue()
        self._rebalance_counter = 0
        self._stop_price: float | None = None

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._channel)

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        close = bar.close.as_double()
        prev_close = self._prev_close.update(close)
        prev_upper = self._prev_upper.update(self._channel.upper)
        iid = self.port_config.instrument_id
        self._rebalance_counter += 1

        if self.portfolio.is_net_long(iid):
            if self._stop_price is not None and close <= self._stop_price:
                self.exit_long()
                self._stop_price = None
                return
            in_channel = self._channel.lower <= close <= self._channel.upper
            near_trend = abs(close - self._channel.trend) / (self._channel.trend + 1e-8) < 0.02
            if in_channel and near_trend:
                self.exit_long()
                self._stop_price = None
            elif self._stop_price is not None:
                self._stop_price = max(self._stop_price, self._channel.lower)
            return

        if self._rebalance_counter < self.config.rebalance_period:
            return
        self._rebalance_counter = 0

        breakout = (
            prev_close is not None
            and prev_upper is not None
            and close > self._channel.upper * self.config.breakout_threshold
            and prev_close <= prev_upper * self.config.breakout_threshold
        )
        if breakout and self._channel.confidence > self.config.min_confidence:
            self.enter_long()
            self._stop_price = self._channel.lower

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        return False
