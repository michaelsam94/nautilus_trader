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

"""Chan Example 3.1: linear mean reversion on price spread with adaptive OLS hedge."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt

from nautilus_trader.examples.strategies.chan_ported.base import ChanPairConfig
from nautilus_trader.examples.strategies.chan_ported.base import ChanPairSpreadStrategy
from nautilus_trader.examples.strategies.chan_ported.indicators import RollingSpreadZScore


class LinearSpreadPairsConfig(ChanPairConfig, frozen=True):
    """Configuration for ``LinearSpreadPairs``."""

    lookback: PositiveInt = 20
    entry_z: PositiveFloat = 1.0
    exit_z: PositiveFloat = 0.0


class LinearSpreadPairs(ChanPairSpreadStrategy):
    """
    OLS spread z-score with linear mean-reversion thresholds.

    Chan (2013) Example 3.1 (price spread), Ch.3 p.82. Distinct from
    ``systematic_trading_ported.pair_trading`` which uses Engle-Granger gate
    and fixed z_entry without proportional sizing semantics.
    """

    def __init__(self, config: LinearSpreadPairsConfig) -> None:
        super().__init__(config)
        self._spread = RollingSpreadZScore(config.lookback)
        self._cfg: LinearSpreadPairsConfig = config

    def _update_spread_signal(self, price1: float, price2: float) -> None:
        self._spread.update_prices(price1, price2)

    def _signal_ready(self) -> bool:
        return self._spread.initialized

    def _spread_signals(self) -> tuple[bool, bool, bool, bool]:
        z = self._spread.value
        entry_long = z < -self._cfg.entry_z
        entry_short = z > self._cfg.entry_z
        exit_long = z >= -self._cfg.exit_z
        exit_short = z <= self._cfg.exit_z
        return entry_long, entry_short, exit_long, exit_short
