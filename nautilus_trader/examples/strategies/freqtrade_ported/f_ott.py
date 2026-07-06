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

"""Port of Freqtrade ``futures/FOttStrategy``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongShortStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import AverageDirectionalIndex
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import OttIndicator


class FOttConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``FOtt``."""

    exit_adx: PositiveFloat = 60.0


class FOtt(FreqtradeLongShortStrategy):
    """OTT VAR crossover futures strategy (ported from FOttStrategy)."""

    def __init__(self, config: FOttConfig) -> None:
        super().__init__(config)
        self._ott = OttIndicator()
        self._adx = AverageDirectionalIndex(14)
        self._var_cross_up = CrossDetector()
        self._var_cross_down = CrossDetector()

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        self.register_indicator_for_bars(bar_type, self._ott)
        self.register_indicator_for_bars(bar_type, self._adx)

    def check_entry(self, bar: Bar) -> bool:
        return self._var_cross_up.crossed_above(self._ott.var, self._ott.ott)

    def check_entry_short(self, bar: Bar) -> bool:
        return self._var_cross_down.crossed_below(self._ott.var, self._ott.ott)

    def check_exit(self, bar: Bar) -> bool:
        return self._adx.adx > self.config.exit_adx

    def check_exit_short(self, bar: Bar) -> bool:
        return self._adx.adx > self.config.exit_adx
