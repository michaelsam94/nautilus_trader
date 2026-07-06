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

"""Chan Example 3.3: Kalman filter dynamic hedge ratio pairs trading."""

from nautilus_trader.config import PositiveFloat

from nautilus_trader.examples.strategies.chan_ported.base import ChanPairConfig
from nautilus_trader.examples.strategies.chan_ported.base import ChanPairSpreadStrategy
from nautilus_trader.examples.strategies.chan_ported.indicators import KalmanHedgeRatio


class KalmanPairsConfig(ChanPairConfig, frozen=True):
    """Configuration for ``KalmanPairs``."""

    entry_z: PositiveFloat = 1.0
    exit_z: PositiveFloat = 0.0
    kalman_delta: PositiveFloat = 1e-4
    observation_variance: PositiveFloat = 1e-3


class KalmanPairs(ChanPairSpreadStrategy):
    """
    Pairs trading with time-varying hedge ratio from Kalman filter.

    Chan (2013) Example 3.3, Ch.3 p.92.
    """

    def __init__(self, config: KalmanPairsConfig) -> None:
        super().__init__(config)
        self._kalman = KalmanHedgeRatio(config.kalman_delta, config.observation_variance)
        self._cfg: KalmanPairsConfig = config

    def _update_spread_signal(self, price1: float, price2: float) -> None:
        self._kalman.update_prices(price1, price2)

    def _signal_ready(self) -> bool:
        return self._kalman.initialized

    def _spread_signals(self) -> tuple[bool, bool, bool, bool]:
        z = self._kalman.z_score
        return (
            z < -self._cfg.entry_z,
            z > self._cfg.entry_z,
            z >= -self._cfg.exit_z,
            z <= self._cfg.exit_z,
        )
