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

"""Port of Freqtrade ``futures/TrendFollowingStrategy``."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import ExponentialMovingAverage
from nautilus_trader.indicators import OnBalanceVolume
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongShortStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import ShiftedValue


class TrendFollowingConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``TrendFollowing``."""

    trend_ema_period: PositiveInt = 20


class TrendFollowing(FreqtradeLongShortStrategy):
    """OBV + EMA trend following (ported from TrendFollowingStrategy)."""

    def __init__(self, config: TrendFollowingConfig) -> None:
        super().__init__(config)
        self._trend = ExponentialMovingAverage(config.trend_ema_period)
        self._obv = OnBalanceVolume()
        self._close_cross_up = CrossDetector()
        self._close_cross_down = CrossDetector()
        self._prev_obv = ShiftedValue()

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        self.register_indicator_for_bars(bar_type, self._trend)
        self.register_indicator_for_bars(bar_type, self._obv)

    def check_entry(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        prev_obv = self._prev_obv.update(self._obv.value)
        return (
            self._close_cross_up.crossed_above(close, self._trend.value)
            and prev_obv is not None
            and self._obv.value > prev_obv
        )

    def check_entry_short(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        prev_obv = self._prev_obv.update(self._obv.value)
        return (
            self._close_cross_down.crossed_below(close, self._trend.value)
            and prev_obv is not None
            and self._obv.value < prev_obv
        )

    def check_exit(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        prev_obv = self._prev_obv.update(self._obv.value)
        return (
            self._close_cross_down.crossed_below(close, self._trend.value)
            and prev_obv is not None
            and self._obv.value > prev_obv
        )

    def check_exit_short(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        prev_obv = self._prev_obv.update(self._obv.value)
        return (
            self._close_cross_up.crossed_above(close, self._trend.value)
            and prev_obv is not None
            and self._obv.value < prev_obv
        )
