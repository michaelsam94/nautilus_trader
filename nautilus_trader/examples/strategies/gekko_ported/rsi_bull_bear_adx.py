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

"""Port of xFFFFF/Gekko-Strategies ``RSI_BULL_BEAR_ADX`` (Tommie Hansen, CC-BY-SA 4.0)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_to_freqtrade
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import (
    AverageDirectionalIndex,
)


class RsiBullBearAdxConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``RsiBullBearAdx``. Defaults from ``RSI_BULL_BEAR_ADX.toml``."""

    sma_long_period: PositiveInt = 1000
    sma_short_period: PositiveInt = 50
    bull_rsi_period: PositiveInt = 10
    bull_rsi_high: PositiveFloat = 80.0
    bull_rsi_low: PositiveFloat = 60.0
    bear_rsi_period: PositiveInt = 15
    bear_rsi_high: PositiveFloat = 50.0
    bear_rsi_low: PositiveFloat = 20.0
    bull_mod_high: float = 5.0
    bull_mod_low: float = -5.0
    bear_mod_high: float = 15.0
    bear_mod_low: float = -5.0
    adx_period: PositiveInt = 3
    adx_high: PositiveFloat = 70.0
    adx_low: PositiveFloat = 50.0


class RsiBullBearAdx(FreqtradeLongOnlyStrategy):
    """
    ``RsiBullBear`` with ADX trend-strength modifiers: strong trends widen the
    exit threshold, weak trends lift the entry threshold.

    The original JS reads the modifiers via ``this.BEAR_MOD_high`` (a bug —
    always ``undefined``, silently disabling the high-side modifier); this port
    applies the configured modifiers as the strategy author documented.
    """

    def __init__(self, config: RsiBullBearAdxConfig) -> None:
        super().__init__(config)
        self._sma_long = SimpleMovingAverage(config.sma_long_period)
        self._sma_short = SimpleMovingAverage(config.sma_short_period)
        self._bull_rsi = RelativeStrengthIndex(config.bull_rsi_period)
        self._bear_rsi = RelativeStrengthIndex(config.bear_rsi_period)
        self._adx = AverageDirectionalIndex(config.adx_period)

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        indicators = (self._sma_long, self._sma_short, self._bull_rsi, self._bear_rsi, self._adx)
        for indicator in indicators:
            self.register_indicator_for_bars(bar_type, indicator)

    def _advice(self) -> str:
        cfg = self.config
        adx = self._adx.adx
        if self._sma_short.value < self._sma_long.value:  # BEAR regime
            rsi = rsi_to_freqtrade(self._bear_rsi.value)
            rsi_hi = cfg.bear_rsi_high
            rsi_low = cfg.bear_rsi_low
            if adx > cfg.adx_high:
                rsi_hi += cfg.bear_mod_high
            elif adx < cfg.adx_low:
                rsi_low += cfg.bear_mod_low
        else:  # BULL regime
            rsi = rsi_to_freqtrade(self._bull_rsi.value)
            rsi_hi = cfg.bull_rsi_high
            rsi_low = cfg.bull_rsi_low
            if adx > cfg.adx_high:
                rsi_hi += cfg.bull_mod_high
            elif adx < cfg.adx_low:
                rsi_low += cfg.bull_mod_low

        if rsi > rsi_hi:
            return "short"
        if rsi < rsi_low:
            return "long"
        return "none"

    def check_entry(self, bar: Bar) -> bool:
        return self._advice() == "long"

    def check_exit(self, bar: Bar) -> bool:
        return self._advice() == "short"
