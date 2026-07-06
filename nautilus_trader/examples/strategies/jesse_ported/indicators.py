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

"""Indicators for Jesse strategy ports."""

from __future__ import annotations

from nautilus_trader.core.correctness import PyCondition
from nautilus_trader.indicators import Indicator
from nautilus_trader.indicators import Stochastics
from nautilus_trader.indicators import StochasticsDMethod
from nautilus_trader.model.data import Bar


class KDJ(Indicator):
    """
    KDJ oscillator (Jesse ``ta.kdj`` defaults: fastk=9, slowk=3, slowd=3).

    ``k``, ``d``, and ``j`` are on a 0-100 scale.
    """

    def __init__(
        self,
        fastk_period: int = 9,
        slowk_period: int = 3,
        slowd_period: int = 3,
    ) -> None:
        PyCondition.positive_int(fastk_period, "fastk_period")
        PyCondition.positive_int(slowk_period, "slowk_period")
        PyCondition.positive_int(slowd_period, "slowd_period")
        super().__init__(params=[fastk_period, slowk_period, slowd_period])
        self._stoch = Stochastics(
            fastk_period,
            slowd_period,
            slowing=slowk_period,
            d_method=StochasticsDMethod.MOVING_AVERAGE,
        )
        self.k: float = 0.0
        self.d: float = 0.0
        self.j: float = 0.0

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        self._stoch.handle_bar(bar)
        if not self._stoch.initialized:
            return
        self.k = self._stoch.value_k
        self.d = self._stoch.value_d
        self.j = 3.0 * self.k - 2.0 * self.d
        if not self.initialized:
            self._set_has_inputs(True)
            self._set_initialized(True)

    def _reset(self) -> None:
        self._stoch.reset()
        self.k = 0.0
        self.d = 0.0
        self.j = 0.0
