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

"""Indicators for vectorbt-backtesting-skills template ports."""

from __future__ import annotations

from nautilus_trader.core.correctness import PyCondition
from nautilus_trader.indicators import AverageTrueRange
from nautilus_trader.indicators import Indicator
from nautilus_trader.indicators import WeightedMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.helpers import RollingStd


class SDA2Bands(Indicator):
    """
    SDA2 trend bands: WMA(3) of HL2 + (open-close), ± STDDEV(7), ± ATR scaling.

    Ported from vectorbt-expert ``assets/sda2/backtest.py``.
    """

    def __init__(
        self,
        wma_period: int = 3,
        stddev_period: int = 7,
        atr_period: int = 2,
    ) -> None:
        PyCondition.positive_int(wma_period, "wma_period")
        PyCondition.positive_int(stddev_period, "stddev_period")
        PyCondition.positive_int(atr_period, "atr_period")
        super().__init__(params=[wma_period, stddev_period, atr_period])
        self._wma = WeightedMovingAverage(wma_period)
        self._std = RollingStd(stddev_period)
        self._atr = AverageTrueRange(atr_period)
        self.derived: float = 0.0
        self.upper: float = 0.0
        self.lower: float = 0.0

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        high = bar.high.as_double()
        low = bar.low.as_double()
        open_ = bar.open.as_double()
        close = bar.close.as_double()
        base = (high + low) / 2.0 + (open_ - close)
        self._wma.update_raw(base)
        self._std.update(base)
        self._atr.handle_bar(bar)
        if not self._wma.initialized or not self._std.initialized or not self._atr.initialized:
            return
        self.derived = self._wma.value
        self.upper = self.derived + self._std.value + (self._atr.value / 1.5)
        self.lower = self.derived - self._std.value - self._atr.value
        if not self.initialized:
            self._set_has_inputs(True)
            self._set_initialized(True)

    def _reset(self) -> None:
        self._wma.reset()
        self._std.reset()
        self._atr.reset()
        self.derived = 0.0
        self.upper = 0.0
        self.lower = 0.0
