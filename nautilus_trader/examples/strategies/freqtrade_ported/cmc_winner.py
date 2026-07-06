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

"""Port of Freqtrade ``berlinguyinca/CMCWinner`` — fixed shift handling."""

from nautilus_trader.indicators import CommodityChannelIndex
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import ShiftedValue
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import ChandeMomentumOscillator
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import MoneyFlowIndex


class CmcWinnerConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``CmcWinner``."""


class CmcWinner(FreqtradeLongOnlyStrategy):
    """CCI + MFI + CMO combination (ported from Freqtrade CMCWinner)."""

    def __init__(self, config: CmcWinnerConfig) -> None:
        super().__init__(config)
        self._cci = CommodityChannelIndex(14)
        self._mfi = MoneyFlowIndex(14)
        self._cmo = ChandeMomentumOscillator(14)
        self._cci_shift = ShiftedValue()
        self._mfi_shift = ShiftedValue()
        self._cmo_shift = ShiftedValue()
        self._prev_cci: float | None = None
        self._prev_mfi: float | None = None
        self._prev_cmo: float | None = None

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        self.register_indicator_for_bars(bar_type, self._cci)
        self.register_indicator_for_bars(bar_type, self._mfi)
        self.register_indicator_for_bars(bar_type, self._cmo)

    def on_bar(self, bar: Bar) -> None:
        if self.indicators_initialized():
            self._prev_cci = self._cci_shift.update(self._cci.value)
            self._prev_mfi = self._mfi_shift.update(self._mfi.value)
            self._prev_cmo = self._cmo_shift.update(self._cmo.value)
        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        if self._prev_cci is None or self._prev_mfi is None or self._prev_cmo is None:
            return False
        return self._prev_cci < -100 and self._prev_mfi < 20 and self._prev_cmo < -50

    def check_exit(self, bar: Bar) -> bool:
        if self._prev_cci is None or self._prev_mfi is None or self._prev_cmo is None:
            return False
        return self._prev_cci > 100 and self._prev_mfi > 80 and self._prev_cmo > 50
