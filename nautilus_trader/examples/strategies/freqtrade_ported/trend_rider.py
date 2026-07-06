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

"""Port of Freqtrade ``TrendRiderStrategy`` (simplified primary-TF subset)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import BollingerBands
from nautilus_trader.indicators import ExponentialMovingAverage
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import RollingMean
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_from_freqtrade
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import AverageDirectionalIndex
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import MacdWithSignal


class TrendRiderConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``TrendRider`` (buy_params defaults)."""

    ema_fast: PositiveInt = 9
    ema_slow: PositiveInt = 16
    rsi_period: PositiveInt = 16
    rsi_pullback_low: PositiveFloat = 30.0
    rsi_pullback_high: PositiveFloat = 65.0
    adx_threshold: PositiveFloat = 18.0
    volume_factor: PositiveFloat = 0.7
    rsi_exit: PositiveFloat = 78.0


class TrendRider(FreqtradeLongOnlyStrategy):
    """
    Trend pullback subset (partial port from TrendRiderStrategy).

    Multi-TF BTC/4h/1d filters, custom_exit cascade, and confirm_trade_entry omitted.
    """

    def __init__(self, config: TrendRiderConfig) -> None:
        super().__init__(config)
        self._ema_fast = ExponentialMovingAverage(config.ema_fast)
        self._ema_slow = ExponentialMovingAverage(config.ema_slow)
        self._ema50 = ExponentialMovingAverage(50)
        self._ema200 = ExponentialMovingAverage(200)
        self._rsi = RelativeStrengthIndex(config.rsi_period)
        self._adx = AverageDirectionalIndex(14)
        self._bb = BollingerBands(20, 2.0)
        self._volume_ema = ExponentialMovingAverage(20)
        self._macd = MacdWithSignal()
        self._ema_cross_up = CrossDetector()
        self._ema_cross_down = CrossDetector()

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        for ind in (
            self._ema_fast,
            self._ema_slow,
            self._ema50,
            self._ema200,
            self._rsi,
            self._adx,
            self._bb,
            self._macd,
        ):
            self.register_indicator_for_bars(bar_type, ind)

    def on_bar(self, bar: Bar) -> None:
        self._volume_ema.update_raw(self.bar_volume(bar))
        super().on_bar(bar)

    def _is_bull(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        return close > self._ema200.value and self._ema50.value > self._ema200.value

    def _volume_ok(self, bar: Bar) -> bool:
        vol_ema = self._volume_ema.value
        if vol_ema <= 0:
            return self.bar_volume(bar) > 0
        return self.bar_volume(bar) / vol_ema > self.config.volume_factor

    def check_entry(self, bar: Bar) -> bool:
        cfg = self.config
        rsi = self._rsi.value
        low = bar.low.as_double()
        close = bar.close.as_double()
        pullback = (
            low <= self._ema_slow.value * 1.02
            and close > self._ema_slow.value
            and close > bar.open.as_double()
        )
        ema_cross = self._ema_cross_up.crossed_above(self._ema_fast.value, self._ema_slow.value)
        return (
            (pullback or ema_cross)
            and self._is_bull(bar)
            and rsi > rsi_from_freqtrade(cfg.rsi_pullback_low)
            and rsi < rsi_from_freqtrade(cfg.rsi_pullback_high)
            and self._adx.adx > cfg.adx_threshold
            and self._adx.plus_di > self._adx.minus_di
            and self._volume_ok(bar)
        )

    def check_exit(self, bar: Bar) -> bool:
        rsi_exit = rsi_from_freqtrade(self.config.rsi_exit)
        bear_cross = self._ema_cross_down.crossed_below(self._ema_fast.value, self._ema_slow.value)
        close = bar.close.as_double()
        return (
            self._rsi.value > rsi_exit
            or (
                bear_cross
                and self._macd.histogram < 0
                and self._rsi.value > rsi_from_freqtrade(50.0)
            )
            or close < self._ema200.value * 0.99
        )
