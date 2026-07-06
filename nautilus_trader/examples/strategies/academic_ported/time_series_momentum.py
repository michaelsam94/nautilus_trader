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

"""Single-asset simplification of QuantConnect time-series momentum."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import RateOfChange
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.academic_ported.indicators import RealizedVolatility
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class TimeSeriesMomentumConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``TimeSeriesMomentum``."""

    lookback_period: PositiveInt = 252
    vol_period: PositiveInt = 60
    max_vol: PositiveFloat = 0.5
    historical_bars_days: PositiveInt = 400


class TimeSeriesMomentum(FreqtradeLongOnlyStrategy):
    """
    Long when trailing return is positive and realized vol is below a cap.

    Upgraded port of ``time-series-momentum-effect.py`` with a vol filter
    proxying multi-asset vol-targeting.
    """

    def __init__(self, config: TimeSeriesMomentumConfig) -> None:
        super().__init__(config)
        self._roc = RateOfChange(config.lookback_period)
        self._vol = RealizedVolatility(config.vol_period)

    def _register_indicators(self) -> None:
        bt = self.port_config.bar_type
        self.register_indicator_for_bars(bt, self._roc)
        self.register_indicator_for_bars(bt, self._vol)

    def check_entry(self, bar: Bar) -> bool:
        if not self._vol.initialized:
            return False
        return self._roc.value > 0 and self._vol.value < self.config.max_vol

    def check_exit(self, bar: Bar) -> bool:
        if not self._vol.initialized:
            return self._roc.value <= 0
        return self._roc.value <= 0 or self._vol.value >= self.config.max_vol
