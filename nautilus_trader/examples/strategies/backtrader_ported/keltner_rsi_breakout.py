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

"""Port of ali-azary ``KeltnerChannelRSIBreakoutStrategy`` (long only)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import AverageTrueRange
from nautilus_trader.indicators import ExponentialMovingAverage
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_from_freqtrade


class KeltnerRsiBreakoutConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``KeltnerRsiBreakout``."""

    ema_period: PositiveInt = 30
    atr_period: PositiveInt = 7
    atr_multiplier: PositiveFloat = 1.0
    rsi_period: PositiveInt = 14
    rsi_low: PositiveFloat = 30.0
    trail_atr_mult: PositiveFloat = 1.0


class KeltnerRsiBreakout(FreqtradeLongOnlyStrategy):
    """
    Close above Keltner upper band with RSI > low threshold; ATR trailing stop exit.

    Ported from ali-azary ``KeltnerChannelRSIBreakoutStrategy`` (long-only subset).
    """

    def __init__(self, config: KeltnerRsiBreakoutConfig) -> None:
        super().__init__(config)
        self._ema = ExponentialMovingAverage(config.ema_period)
        self._atr = AverageTrueRange(config.atr_period)
        self._rsi = RelativeStrengthIndex(config.rsi_period)
        self._trail_stop: float | None = None

    def _register_indicators(self) -> None:
        bt = self.port_config.bar_type
        self.register_indicator_for_bars(bt, self._ema)
        self.register_indicator_for_bars(bt, self._atr)
        self.register_indicator_for_bars(bt, self._rsi)

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        close = bar.close.as_double()
        upper = self._ema.value + self._atr.value * self.config.atr_multiplier
        iid = self.port_config.instrument_id
        rsi_thresh = rsi_from_freqtrade(self.config.rsi_low)

        if self.portfolio.is_net_long(iid):
            new_stop = close - self._atr.value * self.config.trail_atr_mult
            if self._trail_stop is None or new_stop > self._trail_stop:
                self._trail_stop = new_stop
            if self._trail_stop is not None and close <= self._trail_stop:
                self.exit_long()
                self._trail_stop = None
        elif close > upper and self._rsi.value > rsi_thresh:
            self.enter_long()
            self._trail_stop = close - self._atr.value * self.config.trail_atr_mult

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        return False
