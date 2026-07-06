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

"""Port of Freqtrade ``BreakEven``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class BreakEvenConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``BreakEven``."""

    min_profit_to_exit: PositiveFloat = 0.01


class BreakEven(FreqtradeLongOnlyStrategy):
    """
    ROI-style break-even closer (ported from Freqtrade BreakEven).

    Never enters; exits long positions when unrealized return exceeds threshold.
    """

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        pnl = self.unrealized_return(bar)
        return pnl is not None and pnl >= self.config.min_profit_to_exit
