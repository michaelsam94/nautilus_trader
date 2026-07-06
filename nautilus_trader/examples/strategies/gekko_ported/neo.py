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

"""Port of xFFFFF/Gekko-Strategies ``NEO``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_to_freqtrade
from nautilus_trader.examples.strategies.gekko_ported.indicators import RateOfChangeSimple


class NeoConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``Neo``. Defaults from ``NEO.toml``."""

    sma_long_period: PositiveInt = 150
    sma_short_period: PositiveInt = 40
    bull_rsi_period: PositiveInt = 10
    bull_rsi_high: PositiveFloat = 80.0
    bull_rsi_low: PositiveFloat = 50.0
    idle_rsi_period: PositiveInt = 12
    idle_rsi_high: PositiveFloat = 65.0
    idle_rsi_low: PositiveFloat = 39.0
    bear_rsi_period: PositiveInt = 15
    bear_rsi_high: PositiveFloat = 50.0
    bear_rsi_low: PositiveFloat = 25.0
    roc_period: PositiveInt = 6
    roc_level: float = 0.0


class Neo(FreqtradeLongOnlyStrategy):
    """
    ``RsiBullBear`` variant that splits the bull regime into idle-bull and
    real-bull by rate of change, each with its own RSI period/thresholds.
    """

    def __init__(self, config: NeoConfig) -> None:
        super().__init__(config)
        self._sma_long = SimpleMovingAverage(config.sma_long_period)
        self._sma_short = SimpleMovingAverage(config.sma_short_period)
        self._bull_rsi = RelativeStrengthIndex(config.bull_rsi_period)
        self._idle_rsi = RelativeStrengthIndex(config.idle_rsi_period)
        self._bear_rsi = RelativeStrengthIndex(config.bear_rsi_period)
        self._roc = RateOfChangeSimple(config.roc_period)

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        indicators = (
            self._sma_long,
            self._sma_short,
            self._bull_rsi,
            self._idle_rsi,
            self._bear_rsi,
            self._roc,
        )
        for indicator in indicators:
            self.register_indicator_for_bars(bar_type, indicator)

    def _advice(self) -> str:
        cfg = self.config
        if self._sma_short.value < self._sma_long.value:  # BEAR regime
            rsi = rsi_to_freqtrade(self._bear_rsi.value)
            high, low = cfg.bear_rsi_high, cfg.bear_rsi_low
        elif self._roc.value <= cfg.roc_level:  # BULL-IDLE regime
            rsi = rsi_to_freqtrade(self._idle_rsi.value)
            high, low = cfg.idle_rsi_high, cfg.idle_rsi_low
        else:  # REAL BULL regime
            rsi = rsi_to_freqtrade(self._bull_rsi.value)
            high, low = cfg.bull_rsi_high, cfg.bull_rsi_low

        if rsi > high:
            return "short"
        if rsi < low:
            return "long"
        return "none"

    def check_entry(self, bar: Bar) -> bool:
        return self._advice() == "long"

    def check_exit(self, bar: Bar) -> bool:
        return self._advice() == "short"
