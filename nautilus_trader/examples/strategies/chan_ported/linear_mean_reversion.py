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

"""Chan Example 2.5: linear mean-reverting strategy on a single price series."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.chan_ported.indicators import RollingZScore
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class LinearMeanReversionConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``LinearMeanReversion``."""

    lookback: PositiveInt = 20
    entry_z: PositiveFloat = 1.0
    exit_z: PositiveFloat = 0.0
    historical_bars_days: PositiveInt = 60


class LinearMeanReversion(FreqtradeLongOnlyStrategy):
    """
    Long when normalized deviation from MA is sufficiently negative; exit at mean.

    Chan (2013) Example 2.5, Ch.2 p.66. Book uses continuous position sizing
    proportional to ``-z``; this port uses threshold entry/exit for Nautilus orders.
    """

    def __init__(self, config: LinearMeanReversionConfig) -> None:
        super().__init__(config)
        self._z = RollingZScore(config.lookback)

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._z)

    def check_entry(self, bar: Bar) -> bool:
        return self._z.value < -self.config.entry_z

    def check_exit(self, bar: Bar) -> bool:
        return self._z.value >= -self.config.exit_z
