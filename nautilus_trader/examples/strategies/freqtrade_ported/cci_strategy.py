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

"""Port of Freqtrade ``berlinguyinca/CCIStrategy``."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import CommodityChannelIndex
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import ChaikinMoneyFlow
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import MoneyFlowIndex


class CciStrategyConfig(FreqtradePortConfig, frozen=True, kw_only=True):
    """Configuration for ``CciStrategy``."""

    resample_bar_type: BarType
    sma_long_period: PositiveInt = 200
    sma_medium_period: PositiveInt = 50
    sma_short_period: PositiveInt = 25
    sma_trend_period: PositiveInt = 100


class CciStrategy(FreqtradeLongOnlyStrategy):
    """
    CCI + CMF + resampled SMA filters (ported from CCIStrategy).

    ``resample_bar_type`` approximates the 5x resampled OHLC (e.g. 5m when primary is 1m).
    """

    def __init__(self, config: CciStrategyConfig) -> None:
        super().__init__(config)
        self._cci_long = CommodityChannelIndex(170)
        self._cci_short = CommodityChannelIndex(34)
        self._rsi = RelativeStrengthIndex(14)
        self._mfi = MoneyFlowIndex(14)
        self._cmf = ChaikinMoneyFlow(20)
        self._sma_long = SimpleMovingAverage(config.sma_long_period)
        self._sma_medium = SimpleMovingAverage(config.sma_medium_period)
        self._sma_short = SimpleMovingAverage(config.sma_short_period)
        self._sma_trend = SimpleMovingAverage(config.sma_trend_period)
        self._resample_close: float = 0.0

    def _register_indicators(self) -> None:
        primary = self.port_config.bar_type
        for ind in (self._cci_long, self._cci_short, self._rsi, self._mfi, self._cmf):
            self.register_indicator_for_bars(primary, ind)
        resample = self.config.resample_bar_type
        for ind in (self._sma_long, self._sma_medium, self._sma_short, self._sma_trend):
            self.register_indicator_for_bars(resample, ind)

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type == self.config.resample_bar_type:
            self._resample_close = bar.close.as_double()
            return
        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        return (
            self._cci_long.value < -100.0
            and self._cci_short.value < -100.0
            and self._cmf.value < -0.1
            and self._mfi.value < 25.0
            and self._sma_medium.value > self._sma_short.value
            and self._sma_long.value < close
        )

    def check_exit(self, bar: Bar) -> bool:
        return (
            self._cci_long.value > 100.0
            and self._cci_short.value > 100.0
            and self._cmf.value > 0.3
            and self._sma_trend.value < self._sma_medium.value < self._sma_short.value
        )
