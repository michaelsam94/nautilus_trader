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

"""Chan Ch.5/6: volatility futures vs equity index intermarket spread."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt

from nautilus_trader.examples.strategies.chan_ported.base import ChanPairConfig
from nautilus_trader.examples.strategies.chan_ported.base import ChanPairSpreadStrategy
from nautilus_trader.examples.strategies.chan_ported.indicators import RollingSpreadZScore


class VolEquitySpreadConfig(ChanPairConfig, frozen=True):
    """Configuration for ``VolEquitySpread``."""

    lookback: PositiveInt = 60
    entry_z: PositiveFloat = 1.5
    exit_z: PositiveFloat = 0.5


class VolEquitySpread(ChanPairSpreadStrategy):
    """
    Mean-reversion on VX-vs-ES style spread (volatility vs equity futures).

    Chan (2013) Ch.5 p.147 and Ch.6 p.161. Uses rolling spread z-score as
    proxy for roll-return divergence between vol and equity index futures.
    """

    def __init__(self, config: VolEquitySpreadConfig) -> None:
        super().__init__(config)
        self._spread = RollingSpreadZScore(config.lookback)
        self._cfg: VolEquitySpreadConfig = config

    def _update_spread_signal(self, price1: float, price2: float) -> None:
        self._spread.update_prices(price1, price2)

    def _signal_ready(self) -> bool:
        return self._spread.initialized

    def _spread_signals(self) -> tuple[bool, bool, bool, bool]:
        z = self._spread.value
        return (
            z < -self._cfg.entry_z,
            z > self._cfg.entry_z,
            abs(z) < self._cfg.exit_z,
            abs(z) < self._cfg.exit_z,
        )
