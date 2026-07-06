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

"""Port of Freqtrade ``MultiMa`` (stacked TEMA conditions)."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import TripleExponentialMovingAverage


class MultiMaConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``MultiMa``."""

    buy_ma_count: PositiveInt = 4
    buy_ma_gap: PositiveInt = 15
    sell_ma_count: PositiveInt = 12
    sell_ma_gap: PositiveInt = 68
    historical_bars_days: PositiveInt = 1000


class MultiMa(FreqtradeLongOnlyStrategy):
    """
    Stacked TEMA entry (faster below slower) and OR-chain TEMA exit.

    Ported from ``user_data/strategies/MultiMa.py``.
    """

    def __init__(self, config: MultiMaConfig) -> None:
        super().__init__(config)
        periods: set[int] = set()
        for count in range(config.buy_ma_count):
            key = count * config.buy_ma_gap
            if key > 1:
                periods.add(key)
        for count in range(config.sell_ma_count):
            key = count * config.sell_ma_gap
            if key > 1:
                periods.add(key)
        self._temas: dict[int, TripleExponentialMovingAverage] = {
            p: TripleExponentialMovingAverage(p) for p in sorted(periods)
        }

    def _register_indicators(self) -> None:
        bt = self.port_config.bar_type
        for tema in self._temas.values():
            self.register_indicator_for_bars(bt, tema)

    def _tema(self, period: int) -> float:
        return self._temas[period].value

    def check_entry(self, bar: Bar) -> bool:
        cfg = self.config
        matched = False
        for ma_count in range(1, cfg.buy_ma_count):
            key = ma_count * cfg.buy_ma_gap
            past_key = (ma_count - 1) * cfg.buy_ma_gap
            if past_key <= 1 or key not in self._temas or past_key not in self._temas:
                continue
            matched = True
            if self._tema(key) >= self._tema(past_key):
                return False
        return matched

    def check_exit(self, bar: Bar) -> bool:
        cfg = self.config
        for ma_count in range(1, cfg.sell_ma_count):
            key = ma_count * cfg.sell_ma_gap
            past_key = (ma_count - 1) * cfg.sell_ma_gap
            if past_key <= 1 or key not in self._temas or past_key not in self._temas:
                continue
            if self._tema(key) > self._tema(past_key):
                return True
        return False
