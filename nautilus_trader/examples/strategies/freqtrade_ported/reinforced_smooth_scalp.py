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

"""Port of Freqtrade ``berlinguyinca/ReinforcedSmoothScalp``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import CommodityChannelIndex
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.indicators import Stochastics
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import stoch_from_freqtrade
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import AverageDirectionalIndex
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import ExponentialMovingAverageOnHigh
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import MoneyFlowIndex


class ReinforcedSmoothScalpConfig(FreqtradePortConfig, frozen=True, kw_only=True):
    """Configuration for ``ReinforcedSmoothScalp`` (hyperopt defaults)."""

    trend_bar_type: BarType
    trend_sma_period: PositiveInt = 50
    buy_adx: PositiveFloat = 32.0
    buy_fastd: PositiveFloat = 30.0
    buy_mfi: PositiveFloat = 22.0
    sell_fastd: PositiveFloat = 79.0
    sell_fastk: PositiveFloat = 70.0
    sell_cci: PositiveFloat = 183.0


class ReinforcedSmoothScalp(FreqtradeLongOnlyStrategy):
    """
    Reinforced smooth scalp with 5x trend SMA (ported from ReinforcedSmoothScalp).

    ``trend_bar_type`` approximates the 5x resample (e.g. 5m when primary is 1m).
    """

    def __init__(self, config: ReinforcedSmoothScalpConfig) -> None:
        super().__init__(config)
        self._ema_high = ExponentialMovingAverageOnHigh(5)
        self._adx = AverageDirectionalIndex(14)
        self._mfi = MoneyFlowIndex(14)
        self._stoch = Stochastics(5, 3, slowing=3)
        self._cci = CommodityChannelIndex(20)
        self._trend_sma = SimpleMovingAverage(config.trend_sma_period)
        self._stoch_cross = CrossDetector()
        self._trend_close: float = 0.0

    def _register_indicators(self) -> None:
        primary = self.port_config.bar_type
        for ind in (self._ema_high, self._adx, self._mfi, self._stoch, self._cci):
            self.register_indicator_for_bars(primary, ind)
        self.register_indicator_for_bars(self.config.trend_bar_type, self._trend_sma)

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type == self.config.trend_bar_type:
            self._trend_close = bar.close.as_double()
            return
        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        cfg = self.config
        stoch_thr = stoch_from_freqtrade(cfg.buy_fastd)
        return (
            self._mfi.value < cfg.buy_mfi
            and self._stoch.value_d < stoch_thr
            and self._adx.adx > cfg.buy_adx
            and self._stoch_cross.crossed_above(self._stoch.value_k, self._stoch.value_d)
            and self._trend_sma.value < self._trend_close
            and self.bar_volume(bar) > 0
        )

    def check_exit(self, bar: Bar) -> bool:
        cfg = self.config
        stoch_k_hi = stoch_from_freqtrade(cfg.sell_fastk)
        stoch_d_hi = stoch_from_freqtrade(cfg.sell_fastd)
        return (
            bar.open.as_double() > self._ema_high.value
            and self._stoch.value_d > stoch_d_hi
            and self._stoch.value_k > stoch_k_hi
            and self._cci.value > cfg.sell_cci
            and self.bar_volume(bar) > 0
        )
