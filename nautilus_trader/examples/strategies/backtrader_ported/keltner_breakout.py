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

"""Port of ali-azary ``KeltnerBreakoutStrategy`` (long only)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import AverageTrueRange
from nautilus_trader.indicators import ExponentialMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import ShiftedValue


class KeltnerBreakoutConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``KeltnerBreakout``."""

    ema_period: PositiveInt = 30
    atr_period: PositiveInt = 7
    atr_multiplier: PositiveFloat = 1.0
    trail_atr_mult: PositiveFloat = 1.0


class KeltnerBreakout(FreqtradeLongOnlyStrategy):
    """
    Prior close above Keltner upper band entry; close below EMA exit.

    Ported from ali-azary ``KeltnerBreakoutStrategy`` (long-only subset).
    """

    def __init__(self, config: KeltnerBreakoutConfig) -> None:
        super().__init__(config)
        self._ema = ExponentialMovingAverage(config.ema_period)
        self._atr = AverageTrueRange(config.atr_period)
        self._prev_close = ShiftedValue()
        self._prev_upper = ShiftedValue()
        self._trail_stop: float | None = None

    def _register_indicators(self) -> None:
        bt = self.port_config.bar_type
        self.register_indicator_for_bars(bt, self._ema)
        self.register_indicator_for_bars(bt, self._atr)

    def _upper(self) -> float:
        return self._ema.value + self._atr.value * self.config.atr_multiplier

    def _middle(self) -> float:
        return self._ema.value

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        close = bar.close.as_double()
        prev_close = self._prev_close.update(close)
        upper = self._upper()
        prev_upper = self._prev_upper.update(upper)
        iid = self.port_config.instrument_id

        if self.portfolio.is_net_long(iid):
            new_stop = close - self._atr.value * self.config.trail_atr_mult
            if self._trail_stop is None or new_stop > self._trail_stop:
                self._trail_stop = new_stop
            if (self._trail_stop is not None and close <= self._trail_stop) or close < self._middle():
                self.exit_long()
                self._trail_stop = None
        elif prev_close is not None and prev_upper is not None and prev_close > prev_upper:
            self.enter_long()
            self._trail_stop = close - self._atr.value * self.config.trail_atr_mult

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        return False
