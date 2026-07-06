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

"""Port of Freqtrade ``PowerTower`` momentum candlestick pattern."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CloseHistory


class PowerTowerConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``PowerTower``."""

    buy_pow: PositiveFloat = 3.849
    sell_pow: PositiveFloat = 3.798


class PowerTower(FreqtradeLongOnlyStrategy):
    """
    Power Tower: close exceeds prior close raised to a power exponent.

    Ported from ``user_data/strategies/PowerTower.py``.
    """

    def __init__(self, config: PowerTowerConfig) -> None:
        super().__init__(config)
        self._closes = CloseHistory(size=6)

    def on_bar(self, bar: Bar) -> None:
        close = bar.close.as_double()
        self._closes.update(close)
        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        c = self._closes
        cfg = self.config
        c0, c1, c2 = c.shifted(0), c.shifted(1), c.shifted(2)
        c3, c4 = c.shifted(3), c.shifted(4)
        if None in (c0, c1, c2, c3, c4):
            return False
        return (
            c0 > c2 ** cfg.buy_pow
            and c1 > c3 ** cfg.buy_pow
            and c2 > c4 ** cfg.buy_pow
        )

    def check_exit(self, bar: Bar) -> bool:
        c = self._closes
        cfg = self.config
        c0, c1, c2 = c.shifted(0), c.shifted(1), c.shifted(2)
        c3, c4 = c.shifted(3), c.shifted(4)
        if None in (c0, c1, c2, c3, c4):
            return False
        return (
            c0 < c2 ** cfg.sell_pow
            or c1 < c3 ** cfg.sell_pow
            or c2 < c4 ** cfg.sell_pow
        )
