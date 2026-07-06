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

"""Port of Freqtrade ``CustomStoplossWithPSAR``."""

from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import ShiftedValue
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import ParabolicSAR


class CustomStoplossWithPsarConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``CustomStoplossWithPsar``."""


class CustomStoplossWithPsar(FreqtradeLongOnlyStrategy):
    """
    PSAR trailing stop example (ported from Freqtrade CustomStoplossWithPSAR).

    Entry when SAR is falling; exit via PSAR stop when close drops below SAR.
    """

    def __init__(self, config: CustomStoplossWithPsarConfig) -> None:
        super().__init__(config)
        self._sar = ParabolicSAR()
        self._prev_sar = ShiftedValue()

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._sar)

    def check_entry(self, bar: Bar) -> bool:
        prev = self._prev_sar.update(self._sar.value)
        return prev is not None and self._sar.value < prev

    def check_exit(self, bar: Bar) -> bool:
        return False

    def check_custom_stoploss(self, bar: Bar) -> bool:
        return bar.close.as_double() < self._sar.value
