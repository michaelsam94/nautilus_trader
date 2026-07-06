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

"""Chan Example 5.2: currency cross-rate z-score mean reversion."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class CurrencyZscoreMrConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``CurrencyZscoreMr``."""

    lookback: PositiveInt = 20
    historical_bars_days: PositiveInt = 90


class CurrencyZscoreMr(FreqtradeLongOnlyStrategy):
    """
    Sign of negative deviation from MA as mean-reversion signal (AUD.CAD style).

    Chan (2013) Example 5.2, Ch.5 p.126. Rollover interest omitted; add funding
    via Nautilus account model for FX carry accuracy.
    """

    def __init__(self, config: CurrencyZscoreMrConfig) -> None:
        super().__init__(config)
        self._ma = SimpleMovingAverage(config.lookback)
        self._prev_z_sign: int = 0

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._ma)

    def check_entry(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        z = close - self._ma.value
        return z < 0

    def check_exit(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        z = close - self._ma.value
        return z >= 0
