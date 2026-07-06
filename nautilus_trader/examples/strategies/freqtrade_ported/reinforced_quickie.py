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

"""Port of Freqtrade ``berlinguyinca/ReinforcedQuickie``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import BollingerBands
from nautilus_trader.indicators import CommodityChannelIndex
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import AverageHistory
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CloseHistory
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import OpenHistory
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import RollingMean
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import ShiftedValue
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import ExponentialMovingAverageOnClose
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import MoneyFlowIndex
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import RollingMaximum
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import RollingMinimum


class ReinforcedQuickieConfig(FreqtradePortConfig, frozen=True, kw_only=True):
    """Configuration for ``ReinforcedQuickie``."""

    trend_bar_type: BarType
    ema_short: PositiveInt = 5
    ema_medium: PositiveInt = 12
    ema_long: PositiveInt = 21
    trend_sma_period: PositiveInt = 25
    volume_period: PositiveInt = 30
    volume_spike_factor: PositiveFloat = 20.0


class ReinforcedQuickie(FreqtradeLongOnlyStrategy):
    """
    Multi-TF reinforced quickie (ported from Freqtrade ReinforcedQuickie).

    ``trend_bar_type`` approximates the resampled 60m SMA filter (12x 5m).
    """

    def __init__(self, config: ReinforcedQuickieConfig) -> None:
        super().__init__(config)
        self._ema5 = ExponentialMovingAverageOnClose(config.ema_short)
        self._ema12 = ExponentialMovingAverageOnClose(config.ema_medium)
        self._ema21 = ExponentialMovingAverageOnClose(config.ema_long)
        self._bb = BollingerBands(20, 2.0)
        self._min12 = RollingMinimum(config.ema_medium)
        self._max12 = RollingMaximum(config.ema_medium)
        self._cci = CommodityChannelIndex(14)
        self._mfi = MoneyFlowIndex(14)
        self._rsi = RelativeStrengthIndex(7)
        self._trend_sma = SimpleMovingAverage(config.trend_sma_period)
        self._volume_mean = RollingMean(config.volume_period)
        self._prev_volume_mean = ShiftedValue()
        self._prev_trend_sma = ShiftedValue()
        self._trend_close: float = 0.0
        self._avg_hist = AverageHistory(8)
        self._low_hist = ShiftedValue()
        self._open_hist = OpenHistory(8)
        self._close_hist = CloseHistory(8)

    def _register_indicators(self) -> None:
        primary = self.port_config.bar_type
        for ind in (
            self._ema5,
            self._ema12,
            self._min12,
            self._max12,
            self._bb,
            self._cci,
            self._mfi,
            self._rsi,
        ):
            self.register_indicator_for_bars(primary, ind)
        self.register_indicator_for_bars(self.config.trend_bar_type, self._trend_sma)

    def on_bar(self, bar: Bar) -> None:
        self._volume_mean.update(self.bar_volume(bar))
        if bar.bar_type == self.config.trend_bar_type:
            self._trend_close = bar.close.as_double()
            return
        self._avg_hist.update(bar)
        self._low_hist.update(bar.low.as_double())
        self._open_hist.update(bar.open.as_double())
        self._close_hist.update(bar.close.as_double())
        super().on_bar(bar)

    def _trend_filter(self, bar: Bar) -> bool:
        prev_vol = self._prev_volume_mean.update(self._volume_mean.value)
        prev_sma = self._prev_trend_sma.update(self._trend_sma.value)
        volume_cap = (
            prev_vol * self.config.volume_spike_factor if prev_vol is not None else float("inf")
        )
        return (
            self.bar_volume(bar) < volume_cap
            and self._trend_sma.value < self._trend_close
            and prev_sma is not None
            and self._trend_sma.value > prev_sma
        )

    def check_entry(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        path_a = (
            close < self._ema5.value
            and close < self._ema12.value
            and close == self._min12.value
            and close <= self._bb.lower
        )
        a5 = self._avg_hist.shifted(5)
        a4 = self._avg_hist.shifted(4)
        a3 = self._avg_hist.shifted(3)
        a2 = self._avg_hist.shifted(2)
        a1 = self._avg_hist.shifted(1)
        a0 = self._avg_hist.shifted(0)
        prev_low = self._low_hist.update(bar.low.as_double())
        if None in (a5, a4, a3, a2, a1, a0, prev_low):
            path_b = False
        else:
            path_b = (
                a5 > a4 > a3 > a2 > a1 < a0
                and prev_low < self._bb.middle
                and self._cci.value < -100.0
                and self._rsi.value * 100 < 30.0
                and self._mfi.value < 30.0
            )
        return (path_a or path_b) and self._trend_filter(bar)

    def check_exit(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        path_a = (
            close > self._ema5.value
            and close > self._ema12.value
            and close >= self._max12.value
            and close >= self._bb.upper
            and self._mfi.value > 80.0
        )
        eight_green = all(
            self._open_hist.shifted(i) is not None
            and self._close_hist.shifted(i) is not None
            and self._open_hist.shifted(i) < self._close_hist.shifted(i)
            for i in range(8)
        )
        return path_a or (eight_green and self._rsi.value * 100 > 70.0)
