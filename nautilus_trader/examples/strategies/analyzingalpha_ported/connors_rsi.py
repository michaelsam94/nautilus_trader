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

"""Port of leosmigel/analyzingalpha Backtrader ConnorsRSI strategy."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.analyzingalpha_ported.indicators import (
    ConnorsRsiComposite,
)
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class ConnorsRsiConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``ConnorsRsi``."""

    rsi_period: PositiveInt = 3
    streak_period: PositiveInt = 2
    rank_period: PositiveInt = 100
    buy_threshold: PositiveFloat = 10.0
    exit_threshold: PositiveFloat = 90.0


class ConnorsRsi(FreqtradeLongOnlyStrategy):
    """
    Larry Connors' composite RSI mean reversion: enter when ConnorsRSI <= 10,
    exit when >= 90.

    Distinct from ``jesse_ported.rsi2.Rsi2`` — composite of price RSI, streak
    RSI, and percent rank, not a plain short-period RSI.
    """

    def __init__(self, config: ConnorsRsiConfig) -> None:
        super().__init__(config)
        self._crsi = ConnorsRsiComposite(
            config.rsi_period,
            config.streak_period,
            config.rank_period,
        )

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._crsi)

    def check_entry(self, bar: Bar) -> bool:
        return self._crsi.value <= self.config.buy_threshold

    def check_exit(self, bar: Bar) -> bool:
        return self._crsi.value >= self.config.exit_threshold
