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

"""Port of xFFFFF/Gekko-Strategies ``RSI_BULL_BEAR`` (Tommie Hansen, CC-BY-SA 4.0)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_to_freqtrade


class RsiBullBearConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``RsiBullBear``. Defaults from ``RSI_BULL_BEAR.toml``."""

    sma_long_period: PositiveInt = 1000
    sma_short_period: PositiveInt = 50
    bull_rsi_period: PositiveInt = 10
    bull_rsi_high: PositiveFloat = 80.0
    bull_rsi_low: PositiveFloat = 60.0
    bear_rsi_period: PositiveInt = 15
    bear_rsi_high: PositiveFloat = 50.0
    bear_rsi_low: PositiveFloat = 20.0


class RsiBullBear(FreqtradeLongOnlyStrategy):
    """
    Regime-switched RSI: SMA short vs long picks bull/bear regime, each regime
    uses its own RSI period and thresholds.

    Gekko ``long`` advice maps to entry; ``short`` advice maps to exit (spot,
    long/flat).
    """

    def __init__(self, config: RsiBullBearConfig) -> None:
        super().__init__(config)
        self._sma_long = SimpleMovingAverage(config.sma_long_period)
        self._sma_short = SimpleMovingAverage(config.sma_short_period)
        self._bull_rsi = RelativeStrengthIndex(config.bull_rsi_period)
        self._bear_rsi = RelativeStrengthIndex(config.bear_rsi_period)

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        for indicator in (self._sma_long, self._sma_short, self._bull_rsi, self._bear_rsi):
            self.register_indicator_for_bars(bar_type, indicator)

    def _advice(self) -> str:
        cfg = self.config
        if self._sma_short.value < self._sma_long.value:  # BEAR regime
            rsi = rsi_to_freqtrade(self._bear_rsi.value)
            if rsi > cfg.bear_rsi_high:
                return "short"
            if rsi < cfg.bear_rsi_low:
                return "long"
        else:  # BULL regime
            rsi = rsi_to_freqtrade(self._bull_rsi.value)
            if rsi > cfg.bull_rsi_high:
                return "short"
            if rsi < cfg.bull_rsi_low:
                return "long"
        return "none"

    def check_entry(self, bar: Bar) -> bool:
        return self._advice() == "long"

    def check_exit(self, bar: Bar) -> bool:
        return self._advice() == "short"
