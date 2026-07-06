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

"""Port of ali-azary ``MLEnhancedADXStrategy`` (rule-based ensemble, long only)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import AverageTrueRange
from nautilus_trader.indicators import BollingerBands
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CloseHistory
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import RollingMean
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_from_freqtrade
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import AverageDirectionalIndex


class MlEnhancedAdxConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``MlEnhancedAdx``."""

    adx_period: PositiveInt = 14
    adx_threshold: PositiveFloat = 20.0
    rsi_period: PositiveInt = 14
    bb_period: PositiveInt = 7
    atr_period: PositiveInt = 14
    atr_multiplier: PositiveFloat = 3.0
    historical_bars_days: PositiveInt = 60


class MlEnhancedAdx(FreqtradeLongOnlyStrategy):
    """
    ADX trend filter with rule-based feature score replacing RandomForest.

    Ported from ali-azary ``MLEnhancedADXStrategy``; sklearn ML omitted.
    """

    def __init__(self, config: MlEnhancedAdxConfig) -> None:
        super().__init__(config)
        self._adx = AverageDirectionalIndex(config.adx_period)
        self._rsi = RelativeStrengthIndex(config.rsi_period)
        self._bb = BollingerBands(config.bb_period, 2.0)
        self._atr = AverageTrueRange(config.atr_period)
        self._sma_short = SimpleMovingAverage(10)
        self._sma_long = SimpleMovingAverage(30)
        self._volume_ma = RollingMean(20)
        self._closes = CloseHistory(11)
        self._trail_stop: float | None = None

    def _register_indicators(self) -> None:
        bt = self.port_config.bar_type
        for ind in (
            self._adx,
            self._rsi,
            self._bb,
            self._atr,
            self._sma_short,
            self._sma_long,
        ):
            self.register_indicator_for_bars(bt, ind)

    def _rule_score(self, bar: Bar, close: float) -> int:
        score = 0
        c5 = self._closes.shifted(5)
        c10 = self._closes.shifted(10)
        if c5 and c5 > 0 and (close - c5) / c5 > 0.01:
            score += 1
        if c10 and c10 > 0 and (close - c10) / c10 > 0.01:
            score += 1
        if self._sma_short.value > 0 and close / self._sma_short.value - 1 > 0:
            score += 1
        if self._sma_long.value > 0 and close / self._sma_long.value - 1 > 0:
            score += 1
        if self._rsi.value > rsi_from_freqtrade(55):
            score += 1
        bb_width = self._bb.upper - self._bb.lower
        if bb_width > 0 and (close - self._bb.middle) / bb_width > 0.3:
            score += 1
        vol_ma = self._volume_ma.value
        if vol_ma > 0 and self.bar_volume(bar) / vol_ma > 1.1:
            score += 1
        if self._atr.value > 0 and self._atr.value / close > 0.01:
            score += 1
        return score

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        close = bar.close.as_double()
        self._closes.update(close)
        self._volume_ma.update(self.bar_volume(bar))
        iid = self.port_config.instrument_id

        if self.portfolio.is_net_long(iid):
            new_stop = close - self._atr.value * self.config.atr_multiplier
            if self._trail_stop is None or new_stop > self._trail_stop:
                self._trail_stop = new_stop
            if self._trail_stop is not None and close <= self._trail_stop:
                self.exit_long()
                self._trail_stop = None
            return

        if self._adx.adx < self.config.adx_threshold:
            return
        if self._adx.plus_di <= self._adx.minus_di:
            return
        if self._rule_score(bar, close) >= 5:
            self.enter_long()
            self._trail_stop = close - self._atr.value * self.config.atr_multiplier

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        return False
