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

"""Port of Freqtrade ``berlinguyinca/SmoothOperator`` (active entry/exit paths only)."""

from nautilus_trader.indicators import CommodityChannelIndex
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import AverageHistory
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CloseHistory
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import OpenHistory
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import ShiftedValue
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_from_freqtrade
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import BollingerBandsOnTypicalPrice
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import MoneyFlowIndex


class SmoothOperatorConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``SmoothOperator``."""


class SmoothOperator(FreqtradeLongOnlyStrategy):
    """
    Smoothed oversold entry (ported from SmoothOperator).

    Commented-out upstream paths omitted; core V-bottom and oversold branches kept.
    """

    def __init__(self, config: SmoothOperatorConfig) -> None:
        super().__init__(config)
        self._cci = CommodityChannelIndex(20)
        self._rsi = RelativeStrengthIndex(14)
        self._mfi = MoneyFlowIndex(14)
        self._bb = BollingerBandsOnTypicalPrice(20, 2.0)
        self._avg = AverageHistory(8)
        self._open_hist = OpenHistory(9)
        self._close_hist = CloseHistory(9)
        self._prev_close = ShiftedValue()
        self._smooth_hist: list[float] = []

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        for ind in (self._cci, self._rsi, self._mfi, self._bb):
            self.register_indicator_for_bars(bar_type, ind)

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type == self.port_config.bar_type:
            self._avg.update(bar)
            self._open_hist.update(bar.open.as_double())
            self._close_hist.update(bar.close.as_double())
        super().on_bar(bar)

    def _eight_green(self) -> bool:
        return all(
            self._open_hist.shifted(i) is not None
            and self._close_hist.shifted(i) is not None
            and self._open_hist.shifted(i) < self._close_hist.shifted(i)
            for i in range(8)
        )

    def check_entry(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        prev_close = self._prev_close.update(close)
        a5, a4, a3, a2, a1, a0 = (
            self._avg.shifted(5),
            self._avg.shifted(4),
            self._avg.shifted(3),
            self._avg.shifted(2),
            self._avg.shifted(1),
            self._avg.shifted(0),
        )
        v_bottom = False
        if None not in (a5, a4, a3, a2, a1, a0):
            v_bottom = (
                a5 > a4 > a3 > a2 > a1 < a0
                and bar.low.as_double() < self._bb.middle
                and self._cci.value < -100.0
                and self._rsi.value < rsi_from_freqtrade(30.0)
            )
        oversold = (
            bar.low.as_double() < self._bb.middle
            and self._cci.value < -200.0
            and self._rsi.value < rsi_from_freqtrade(30.0)
            and self._mfi.value < 30.0
        )
        extreme = (
            self._mfi.value < 10.0
            and self._cci.value < -150.0
            and self._rsi.value * 100.0 < self._mfi.value
        )
        rising = prev_close is not None and close > prev_close
        return rising and (v_bottom or oversold or extreme)

    def check_exit(self, bar: Bar) -> bool:
        return (
            self._eight_green()
            or (self._cci.value > 200.0 and self._rsi.value > rsi_from_freqtrade(70.0))
        )
