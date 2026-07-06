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

"""Port of xFFFFF/Gekko-Strategies ``buyatsellat``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class BuyAtSellAtConfig(FreqtradePortConfig, frozen=True):
    """
    Configuration for ``BuyAtSellAt``. Defaults from the hardcoded JS constants.

    Multipliers are relative to the price at the last action (advice close, as
    in the original — not the fill price).
    """

    buy_at: PositiveFloat = 1.05
    sell_at: PositiveFloat = 0.97
    stop_loss_pct: PositiveFloat = 0.95
    sell_at_up: PositiveFloat = 1.01


class BuyAtSellAt(FreqtradeLongOnlyStrategy):
    """
    Mechanical percent flipper: after a sell, rebuy when price drops ``sell_at``
    below or rises ``sell_at_up`` above the last action price; after a buy, sell
    at ``buy_at`` profit or ``stop_loss_pct`` stop.

    No indicators — a 2-bar SMA is registered only to satisfy the base class
    warm-up gate.
    """

    def __init__(self, config: BuyAtSellAtConfig) -> None:
        super().__init__(config)
        self._warmup = SimpleMovingAverage(2)
        self._last_action_price = float("inf")

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._warmup)

    def check_entry(self, bar: Bar) -> bool:
        cfg = self.config
        close = bar.close.as_double()
        rebuy_low = self._last_action_price * cfg.sell_at
        rebuy_high = self._last_action_price * cfg.sell_at_up
        if close < rebuy_low or close > rebuy_high:
            self._last_action_price = close
            return True
        return False

    def check_exit(self, bar: Bar) -> bool:
        cfg = self.config
        close = bar.close.as_double()
        take_profit = self._last_action_price * cfg.buy_at
        stop_loss = self._last_action_price * cfg.stop_loss_pct
        if close > take_profit or close < stop_loss:
            self._last_action_price = close
            return True
        return False
