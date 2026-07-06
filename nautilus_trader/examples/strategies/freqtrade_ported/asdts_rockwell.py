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

"""Port of Freqtrade ``berlinguyinca/ASDTSRockwellTrading``."""

from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import MacdWithSignal


class AsdtsRockwellConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``AsdtsRockwell``."""


class AsdtsRockwell(FreqtradeLongOnlyStrategy):
    """MACD above zero and signal (ported from ASDTSRockwellTrading)."""

    def __init__(self, config: AsdtsRockwellConfig) -> None:
        super().__init__(config)
        self._macd = MacdWithSignal()

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._macd)

    def check_entry(self, bar: Bar) -> bool:
        return self._macd.macd > 0 and self._macd.macd > self._macd.signal

    def check_exit(self, bar: Bar) -> bool:
        return self._macd.macd < self._macd.signal
