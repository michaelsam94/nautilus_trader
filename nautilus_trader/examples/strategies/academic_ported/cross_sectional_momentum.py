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

"""12-1 month momentum (UMD) single-asset signal."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.academic_ported.indicators import LaggedReturn
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class CrossSectionalMomentumConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``CrossSectionalMomentum``."""

    lookback_days: PositiveInt = 252
    skip_days: PositiveInt = 21
    historical_bars_days: PositiveInt = 400


class CrossSectionalMomentum(FreqtradeLongOnlyStrategy):
    """
    Long when 12-month return skipping the most recent month is positive.

    Simplified port of ``momentum-factor-effect-in-stocks.py``.
    """

    def __init__(self, config: CrossSectionalMomentumConfig) -> None:
        super().__init__(config)
        self._momentum = LaggedReturn(config.lookback_days, config.skip_days)

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._momentum)

    def check_entry(self, bar: Bar) -> bool:
        return self._momentum.value > 0

    def check_exit(self, bar: Bar) -> bool:
        return self._momentum.value <= 0
