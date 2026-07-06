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

"""Port of Freqtrade ``Diamond``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import ShiftedValue


class DiamondConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``Diamond`` (hyperopt defaults)."""

    buy_fast_key: str = "high"
    buy_slow_key: str = "volume"
    buy_horizontal_push: PositiveInt = 7
    buy_vertical_push: PositiveFloat = 0.942
    sell_fast_key: str = "high"
    sell_slow_key: str = "low"
    sell_horizontal_push: PositiveInt = 10
    sell_vertical_push: PositiveFloat = 1.184


class Diamond(FreqtradeLongOnlyStrategy):
    """Pure OHLCV crossover strategy (ported from Freqtrade Diamond)."""

    def __init__(self, config: DiamondConfig) -> None:
        super().__init__(config)
        self._bar_history: list[Bar] = []
        self._entry_cross = CrossDetector()
        self._exit_cross = CrossDetector()

    def _bar_field(self, bar: Bar, key: str) -> float:
        if key == "open":
            return bar.open.as_double()
        if key == "high":
            return bar.high.as_double()
        if key == "low":
            return bar.low.as_double()
        if key == "close":
            return bar.close.as_double()
        if key == "volume":
            return self.bar_volume(bar)
        raise ValueError(f"Unsupported bar field: {key}")

    def _shifted_field(self, key: str, push: int) -> float | None:
        if len(self._bar_history) <= push:
            return None
        return self._bar_field(self._bar_history[-(push + 1)], key)

    def on_bar(self, bar: Bar) -> None:
        self._bar_history.append(bar)
        if len(self._bar_history) > 500:
            self._bar_history.pop(0)
        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        cfg = self.config
        fast = self._shifted_field(cfg.buy_fast_key, cfg.buy_horizontal_push)
        slow = self._bar_field(bar, cfg.buy_slow_key) * cfg.buy_vertical_push
        if fast is None:
            return False
        return self._entry_cross.crossed_above(fast, slow)

    def check_exit(self, bar: Bar) -> bool:
        cfg = self.config
        fast = self._shifted_field(cfg.sell_fast_key, cfg.sell_horizontal_push)
        slow = self._bar_field(bar, cfg.sell_slow_key) * cfg.sell_vertical_push
        if fast is None:
            return False
        return self._exit_cross.crossed_below(fast, slow)
