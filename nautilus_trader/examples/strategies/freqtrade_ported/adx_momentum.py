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

"""Port of Freqtrade ``berlinguyinca/ADXMomentum``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import RateOfChange
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import AverageDirectionalIndex


class AdxMomentumConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``AdxMomentum``."""

    adx_period: PositiveInt = 14
    di_period: PositiveInt = 25
    mom_period: PositiveInt = 14
    adx_threshold: PositiveFloat = 25.0
    di_threshold: PositiveFloat = 25.0


class AdxMomentum(FreqtradeLongOnlyStrategy):
    """ADX + momentum + DI strategy (ported from Freqtrade ADXMomentum)."""

    def __init__(self, config: AdxMomentumConfig) -> None:
        super().__init__(config)
        self._adx = AverageDirectionalIndex(config.adx_period)
        self._mom = RateOfChange(config.mom_period)

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        self.register_indicator_for_bars(bar_type, self._adx)
        self.register_indicator_for_bars(bar_type, self._mom)

    def check_entry(self, bar: Bar) -> bool:
        return (
            self._adx.adx > self.config.adx_threshold
            and self._mom.value > 0
            and self._adx.plus_di > self.config.di_threshold
            and self._adx.plus_di > self._adx.minus_di
        )

    def check_exit(self, bar: Bar) -> bool:
        return (
            self._adx.adx > self.config.adx_threshold
            and self._mom.value < 0
            and self._adx.minus_di > self.config.di_threshold
            and self._adx.plus_di < self._adx.minus_di
        )
