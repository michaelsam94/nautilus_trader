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

"""Single-asset 52-week high proximity signal."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.academic_ported.indicators import RollingMaximum
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class Weeks52HighConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``Weeks52High``."""

    lookback_period: PositiveInt = 252
    min_prilag: PositiveFloat = 0.95
    historical_bars_days: PositiveInt = 400


class Weeks52High(FreqtradeLongOnlyStrategy):
    """
    Long when close is near its rolling 52-week high (PRILAG proxy).

    Simplified port of ``52-weeks-high-effect-in-stocks.py`` (industry-ranked
    long/short universe in source).
    """

    def __init__(self, config: Weeks52HighConfig) -> None:
        super().__init__(config)
        self._max_close = RollingMaximum(config.lookback_period)

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._max_close)

    def check_entry(self, bar: Bar) -> bool:
        if self._max_close.value <= 0:
            return False
        prilag = bar.close.as_double() / self._max_close.value
        return prilag >= self.config.min_prilag

    def check_exit(self, bar: Bar) -> bool:
        if self._max_close.value <= 0:
            return False
        prilag = bar.close.as_double() / self._max_close.value
        return prilag < self.config.min_prilag
