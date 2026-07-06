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

"""Full port of je-suis-tm/quant-trading ``Shooting Star`` (short entry)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongShortStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.systematic_trading_ported.indicators import ShootingStarPattern


class ShootingStarShortConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``ShootingStarShort``."""

    lower_bound: PositiveFloat = 0.2
    body_size: PositiveFloat = 0.5
    body_lookback: PositiveInt = 20
    stop_threshold: PositiveFloat = 0.05
    holding_period: PositiveInt = 7
    historical_bars_days: PositiveInt = 60


class ShootingStarShort(FreqtradeLongShortStrategy):
    """
    Short on confirmed shooting-star pattern with stop and max holding period.

    Ported from je-suis-tm/quant-trading ``Shooting Star backtest.py``.
    Complements ``ShootingStarExit`` (long-only bearish exit signal).
    """

    def __init__(self, config: ShootingStarShortConfig) -> None:
        super().__init__(config)
        self._pattern = ShootingStarPattern(
            config.lower_bound,
            config.body_size,
            config.body_lookback,
        )
        self._bars_in_trade = 0
        self._entry_price: float | None = None

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._pattern)

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        return False

    def check_entry_short(self, bar: Bar) -> bool:
        return self._pattern.detected

    def check_exit_short(self, bar: Bar) -> bool:
        if self._entry_price is None:
            return False
        close = bar.close.as_double()
        if abs(close / self._entry_price - 1.0) > self.config.stop_threshold:
            return True
        self._bars_in_trade += 1
        return self._bars_in_trade >= self.config.holding_period

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        iid = self.port_config.instrument_id
        if self.portfolio.is_net_short(iid) and self._entry_price is None:
            self._entry_price = bar.close.as_double()
            self._bars_in_trade = 0

        if self.portfolio.is_net_short(iid):
            if self.check_custom_stoploss_short(bar) or self.check_exit_short(bar):
                self.exit_short()
                self._entry_price = None
                self._bars_in_trade = 0
            return

        if self.portfolio.is_flat(iid) and self.check_entry_short(bar):
            self.enter_short()
            self._entry_price = bar.close.as_double()
            self._bars_in_trade = 0
