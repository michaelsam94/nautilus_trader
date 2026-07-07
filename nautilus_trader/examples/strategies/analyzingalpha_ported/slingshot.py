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

"""Port of leosmigel/analyzingalpha scot1and slingshot setup notebook."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import ExponentialMovingAverage
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import (
    ExponentialMovingAverageOnHigh,
)


class SlingshotConfig(FreqtradePortConfig, frozen=True, kw_only=True):
    """
    Configuration for ``Slingshot``.

    ``bar_type`` is the trigger timeframe (1h in the source); ``daily_bar_type``
    provides trend/pullback context and the stop anchor.
    """

    daily_bar_type: BarType
    sma_trend_period: PositiveInt = 50
    ema_pullback_period: PositiveInt = 10
    ema_trigger_period: PositiveInt = 4
    risk_reward: PositiveFloat = 2.0


class Slingshot(FreqtradeLongOnlyStrategy):
    """
    scot1and's slingshot setup: daily uptrend (close > SMA50) in pullback
    (close < EMA10), triggered intraday when close crosses above the EMA4 of
    highs. Stop at the prior daily low; take profit at ``risk_reward`` R.
    """

    def __init__(self, config: SlingshotConfig) -> None:
        super().__init__(config)
        self._sma_trend = SimpleMovingAverage(config.sma_trend_period)
        self._ema_pullback = ExponentialMovingAverage(config.ema_pullback_period)
        self._ema_trigger = ExponentialMovingAverageOnHigh(config.ema_trigger_period)
        self._cross = CrossDetector()
        self._daily_close: float | None = None
        self._daily_low: float | None = None
        self._entry_price: float | None = None
        self._stop_price: float | None = None

    def all_bar_types(self) -> tuple[BarType, ...]:
        return (
            self.port_config.bar_type,
            self.config.daily_bar_type,
            *self.port_config.informative_bar_types,
        )

    def _register_indicators(self) -> None:
        daily = self.config.daily_bar_type
        self.register_indicator_for_bars(daily, self._sma_trend)
        self.register_indicator_for_bars(daily, self._ema_pullback)
        self.register_indicator_for_bars(self.port_config.bar_type, self._ema_trigger)

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type == self.config.daily_bar_type:
            self._daily_close = bar.close.as_double()
            self._daily_low = bar.low.as_double()
        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        if self._daily_close is None or self._daily_low is None:
            return False
        in_setup = (
            self._daily_close > self._sma_trend.value
            and self._daily_close < self._ema_pullback.value
        )
        close = bar.close.as_double()
        triggered = self._cross.crossed_above(close, self._ema_trigger.value)
        if not (in_setup and triggered):
            return False
        self._entry_price = close
        self._stop_price = self._daily_low
        return True

    def check_exit(self, bar: Bar) -> bool:
        if self._entry_price is None or self._stop_price is None:
            return False
        close = bar.close.as_double()
        if close < self._stop_price:
            return True
        risk = self._entry_price - self._stop_price
        if risk > 0 and close > self._entry_price + risk * self.config.risk_reward:
            return True
        return False
