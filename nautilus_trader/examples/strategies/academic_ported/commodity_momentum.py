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

"""12-month commodity momentum on a single continuous contract."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import RateOfChange
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class CommodityMomentumConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``CommodityMomentum``."""

    lookback_period: PositiveInt = 252
    historical_bars_days: PositiveInt = 400


class CommodityMomentum(FreqtradeLongOnlyStrategy):
    """
    Long when 12-month rate-of-change is positive.

    Single-instrument port of ``momentum-effect-in-commodities.py``.
    """

    def __init__(self, config: CommodityMomentumConfig) -> None:
        super().__init__(config)
        self._roc = RateOfChange(config.lookback_period)

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._roc)

    def check_entry(self, bar: Bar) -> bool:
        return self._roc.value > 0

    def check_exit(self, bar: Bar) -> bool:
        return self._roc.value <= 0
