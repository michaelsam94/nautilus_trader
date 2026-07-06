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

"""Port of Freqtrade ``berlinguyinca/Low_BB``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import BollingerBands
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class LowBbConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``LowBb``."""

    bb_period: PositiveInt = 20
    bb_std: PositiveFloat = 2.0
    lower_band_factor: PositiveFloat = 0.98


class LowBb(FreqtradeLongOnlyStrategy):
    """
    Buy when close crosses below scaled lower Bollinger band.

    Exit signals in the original use trailing stop / ROI only; not ported here.
    """

    def __init__(self, config: LowBbConfig) -> None:
        super().__init__(config)
        self._bb = BollingerBands(config.bb_period, config.bb_std)

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._bb)

    def check_entry(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        return close <= self.config.lower_band_factor * self._bb.lower

    def check_exit(self, bar: Bar) -> bool:
        return False
