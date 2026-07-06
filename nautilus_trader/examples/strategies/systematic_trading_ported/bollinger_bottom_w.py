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

"""Port of je-suis-tm/quant-trading Bollinger Bands bottom-W pattern (simplified)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import BollingerBands
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class BollingerBottomWConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``BollingerBottomW``."""

    bb_period: PositiveInt = 20
    bb_std: PositiveFloat = 2.0
    lookback: PositiveInt = 75
    band_tolerance: PositiveFloat = 0.0001


class BollingerBottomW(FreqtradeLongOnlyStrategy):
    """
    Simplified double-bottom / W pattern on Bollinger Bands.

    Source: je-suis-tm/quant-trading ``Bollinger Bands Pattern Recognition backtest.py``.
    Full five-node W scan is approximated with touch-lower-band then upper-band breakout.
    """

    def __init__(self, config: BollingerBottomWConfig) -> None:
        super().__init__(config)
        self._bb = BollingerBands(config.bb_period, config.bb_std)
        self._lows: list[float] = []
        self._lower_touches: list[bool] = []
        self._saw_lower_touch: bool = False

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._bb)

    def check_entry(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        tol = self.config.band_tolerance
        at_lower = abs(close - self._bb.lower) < tol or close <= self._bb.lower
        if at_lower:
            self._saw_lower_touch = True
            return False
        if self._saw_lower_touch and close > self._bb.upper:
            self._saw_lower_touch = False
            return True
        return False

    def check_exit(self, bar: Bar) -> bool:
        bandwidth = self._bb.upper - self._bb.lower
        if bandwidth <= self.config.band_tolerance:
            return True
        close = bar.close.as_double()
        return close < self._bb.middle
