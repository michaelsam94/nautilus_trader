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

"""Port of Freqtrade ``berlinguyinca/BinHV45``."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import BollingerBands
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import ShiftedValue


class BinHv45Config(FreqtradePortConfig, frozen=True):
    """Configuration for ``BinHv45`` (hyperopt defaults)."""

    buy_bbdelta: PositiveInt = 7
    buy_closedelta: PositiveInt = 17
    buy_tail: PositiveInt = 25
    bb_period: PositiveInt = 40


class BinHv45(FreqtradeLongOnlyStrategy):
    """BB delta wick entry (ported from BinHV45; no exit signal in upstream)."""

    def __init__(self, config: BinHv45Config) -> None:
        super().__init__(config)
        self._bb = BollingerBands(config.bb_period, 2.0)
        self._prev_close = ShiftedValue()
        self._prev_lower = ShiftedValue()

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._bb)

    def check_entry(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        prev_close = self._prev_close.update(close)
        prev_lower = self._prev_lower.update(self._bb.lower)
        if prev_close is None or prev_lower is None or prev_lower <= 0:
            return False
        bbdelta = abs(self._bb.middle - self._bb.lower)
        closedelta = abs(close - prev_close)
        tail = abs(close - bar.low.as_double())
        cfg = self.config
        return (
            bbdelta > close * cfg.buy_bbdelta / 1000.0
            and closedelta > close * cfg.buy_closedelta / 1000.0
            and tail < bbdelta * cfg.buy_tail / 1000.0
            and close < prev_lower
            and close <= prev_close
        )

    def check_exit(self, bar: Bar) -> bool:
        return False
