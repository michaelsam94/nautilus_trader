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

"""Port of ali-azary ``RegimeFilteredTrendStrategy`` (long only)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import AverageTrueRange
from nautilus_trader.indicators import BollingerBands
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import AverageDirectionalIndex


class RegimeFilteredTrendConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``RegimeFilteredTrend``."""

    ma_fast: PositiveInt = 7
    ma_slow: PositiveInt = 30
    adx_period: PositiveInt = 14
    adx_trending_threshold: PositiveFloat = 20.0
    bb_period: PositiveInt = 7
    bb_width_threshold: PositiveFloat = 0.01
    vol_trending_threshold: PositiveFloat = 0.01
    regime_confirmation: PositiveInt = 3
    trail_atr_mult: PositiveFloat = 3.0
    range_atr_mult: PositiveFloat = 1.0
    historical_bars_days: PositiveInt = 60


class RegimeFilteredTrend(FreqtradeLongOnlyStrategy):
    """
    MA crossover entries only in confirmed trending regime (long only).

    Ported from ali-azary ``RegimeFilteredTrendStrategy``; HMM-style logic
    replaced by ADX/BB-width/volatility/MA-separation voting.
    """

    def __init__(self, config: RegimeFilteredTrendConfig) -> None:
        super().__init__(config)
        self._ma_fast = SimpleMovingAverage(config.ma_fast)
        self._ma_slow = SimpleMovingAverage(config.ma_slow)
        self._adx = AverageDirectionalIndex(config.adx_period)
        self._bb = BollingerBands(config.bb_period, 2.0)
        self._atr = AverageTrueRange(config.adx_period)
        self._cross = CrossDetector()
        self._regime_history: list[str] = []
        self._current_regime = "unknown"
        self._trail_stop: float | None = None
        self._volatility_history: list[float] = []

    def _register_indicators(self) -> None:
        bt = self.port_config.bar_type
        for ind in (self._ma_fast, self._ma_slow, self._adx, self._bb, self._atr):
            self.register_indicator_for_bars(bt, ind)

    def _classify_regime(self, close: float) -> str:
        trending_signals = 0
        if self._adx.adx > self.config.adx_trending_threshold:
            trending_signals += 1
        bb_width = (self._bb.upper - self._bb.lower) / (self._bb.middle + 1e-8)
        if bb_width > self.config.bb_width_threshold:
            trending_signals += 1
        if close > 0 and self._atr.value / close > self.config.vol_trending_threshold:
            trending_signals += 1
        ma_sep = abs(self._ma_fast.value - self._ma_slow.value) / (self._ma_slow.value + 1e-8)
        if ma_sep > 0.02:
            trending_signals += 1
        confidence = trending_signals / 4.0
        if confidence >= 0.75:
            return "trending"
        if confidence <= 0.25:
            return "ranging"
        return "uncertain"

    def _trail_multiplier(self) -> float:
        if self._current_regime == "trending":
            mult = self.config.trail_atr_mult
            if len(self._volatility_history) >= 5:
                current = self._volatility_history[-1]
                avg = sum(self._volatility_history[-10:]) / min(10, len(self._volatility_history))
                if avg > 0 and current > avg * 1.2:
                    mult *= 1.3
                elif avg > 0 and current < avg * 0.8:
                    mult *= 0.8
            return mult
        return self.config.range_atr_mult

    def _update_regime(self, close: float) -> None:
        new_regime = self._classify_regime(close)
        self._regime_history.append(new_regime)
        if len(self._regime_history) > self.config.regime_confirmation * 2:
            self._regime_history = self._regime_history[-self.config.regime_confirmation * 2 :]
        if len(self._regime_history) >= self.config.regime_confirmation:
            recent = self._regime_history[-self.config.regime_confirmation :]
            if all(r == new_regime for r in recent):
                self._current_regime = new_regime

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        close = bar.close.as_double()
        if close > 0:
            self._volatility_history.append(self._atr.value / close)
            if len(self._volatility_history) > 20:
                self._volatility_history = self._volatility_history[-20:]
        self._update_regime(close)
        iid = self.port_config.instrument_id

        if self.portfolio.is_net_long(iid):
            mult = self._trail_multiplier()
            new_stop = close - self._atr.value * mult
            if self._trail_stop is None or new_stop > self._trail_stop:
                self._trail_stop = new_stop
            if (
                (self._trail_stop is not None and close <= self._trail_stop)
                or self._ma_fast.value < self._ma_slow.value
                or self._current_regime == "ranging"
            ):
                self.exit_long()
                self._trail_stop = None
            return

        if self._current_regime != "trending":
            return
        if self._cross.crossed_above(self._ma_fast.value, self._ma_slow.value):
            self.enter_long()
            self._trail_stop = close - self._atr.value * self._trail_multiplier()

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        return False
