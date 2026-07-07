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

"""Port of leosmigel/analyzingalpha crypto price-shear mean-reversion notebook."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import ExponentialMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.analyzingalpha_ported.indicators import WilderAtr
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class PriceShearConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``PriceShear``."""

    ema_period: PositiveInt = 12
    atr_period: PositiveInt = 12
    shear_atr_multiple: PositiveFloat = 2.5


class PriceShear(FreqtradeLongOnlyStrategy):
    """
    Shock mean reversion: when price is displaced more than ``shear_atr_multiple``
    ATRs *below* its EMA (a fresh "shear"), buy the dislocation and exit on the
    next bar.

    The source notebook holds exactly one bar per signal; this port mirrors that
    by exiting on the first bar after entry.
    """

    def __init__(self, config: PriceShearConfig) -> None:
        super().__init__(config)
        self._ema = ExponentialMovingAverage(config.ema_period)
        self._atr = WilderAtr(config.atr_period)
        self._prev_shear = False
        self._fresh_shear = False

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        self.register_indicator_for_bars(bar_type, self._ema)
        self.register_indicator_for_bars(bar_type, self._atr)

    def on_bar(self, bar: Bar) -> None:
        # Track shear state on every primary bar (whether long or flat) so the
        # freshness flag stays correct across the one-bar holding period
        if bar.bar_type == self.port_config.bar_type and self.indicators_initialized():
            close = bar.close.as_double()
            displaced = abs(close - self._ema.value) > (
                self._atr.value * self.config.shear_atr_multiple
            )
            shear = displaced and close < self._ema.value
            self._fresh_shear = shear and not self._prev_shear
            self._prev_shear = shear
        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        return self._fresh_shear

    def check_exit(self, bar: Bar) -> bool:
        return True  # one-bar hold, as in the source notebook
