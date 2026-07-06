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

"""Port of Freqtrade ``Heracles`` (fixed hyperopt genome)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import DonchianChannelPercent
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import KeltnerChannelWidth


class HeraclesConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``Heracles`` (default buy_params)."""

    buy_div_min: PositiveFloat = 0.16
    buy_div_max: PositiveFloat = 0.75
    buy_indicator_shift: PositiveInt = 15
    buy_crossed_indicator_shift: PositiveInt = 9


class Heracles(FreqtradeLongOnlyStrategy):
    """Single-genome Heracles (ported from Heracles)."""

    def __init__(self, config: HeraclesConfig) -> None:
        super().__init__(config)
        self._kcw = KeltnerChannelWidth(20, 10)
        self._dcp = DonchianChannelPercent(10)
        self._dcp_shifts: list[float] = []
        self._kcw_shifts: list[float] = []

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        self.register_indicator_for_bars(bar_type, self._kcw)
        self.register_indicator_for_bars(bar_type, self._dcp)

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type == self.port_config.bar_type:
            self._dcp_shifts.insert(0, self._dcp.value)
            self._kcw_shifts.insert(0, self._kcw.value)
            max_len = max(self.config.buy_indicator_shift, self.config.buy_crossed_indicator_shift) + 1
            self._dcp_shifts = self._dcp_shifts[:max_len]
            self._kcw_shifts = self._kcw_shifts[:max_len]
        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        cfg = self.config
        if len(self._dcp_shifts) <= cfg.buy_indicator_shift:
            return False
        if len(self._kcw_shifts) <= cfg.buy_crossed_indicator_shift:
            return False
        kcw_at = self._kcw_shifts[cfg.buy_crossed_indicator_shift]
        dcp_at = self._dcp_shifts[cfg.buy_indicator_shift]
        if kcw_at == 0:
            return False
        ratio = dcp_at / kcw_at
        return cfg.buy_div_min <= ratio <= cfg.buy_div_max

    def check_exit(self, bar: Bar) -> bool:
        return False
