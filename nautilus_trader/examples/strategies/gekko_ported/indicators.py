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

"""
Python indicators used by ported Gekko strategies.

Gekko strategies use Tulip indicators; built-in Nautilus indicators and the
``freqtrade_ported.indicators`` module cover most needs. This module fills the
remaining gaps.
"""

from __future__ import annotations

from collections import deque

from nautilus_trader.core.correctness import PyCondition
from nautilus_trader.indicators import Indicator
from nautilus_trader.model.data import Bar


class RateOfChangeSimple(Indicator):
    """
    Tulip-compatible rate of change: ``(close - close[n]) / close[n]``.

    Parameters
    ----------
    period : int
        The lookback period ``n``.
    """

    def __init__(self, period: int) -> None:
        PyCondition.positive_int(period, "period")
        super().__init__(params=[period])
        self.period = period
        self.value: float = 0.0
        self._closes: deque[float] = deque(maxlen=period + 1)

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        close = bar.close.as_double()
        self._closes.append(close)
        self._set_has_inputs(True)
        if len(self._closes) == self._closes.maxlen:
            oldest = self._closes[0]
            self.value = (close - oldest) / oldest if oldest != 0 else 0.0
            self._set_initialized(True)

    def _reset(self) -> None:
        self.value = 0.0
        self._closes.clear()
