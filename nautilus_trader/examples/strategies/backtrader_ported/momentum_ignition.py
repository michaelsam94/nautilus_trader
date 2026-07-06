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

"""Port of ali-azary ``MomentumIgnitionStrategy`` (long only)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import RateOfChange
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import RollingMean
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import RollingStd


class MomentumIgnitionConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``MomentumIgnition``."""

    consolidation_period: PositiveInt = 30
    consolidation_threshold: PositiveFloat = 0.1
    roc_period: PositiveInt = 7
    roc_ma_period: PositiveInt = 30
    roc_breakout_std: PositiveFloat = 1.0
    trend_period: PositiveInt = 30


class MomentumIgnition(FreqtradeLongOnlyStrategy):
    """
    Low-volatility consolidation plus ROC statistical breakout (long only).

    Ported from ali-azary ``MomentumIgnitionStrategy``.
    ATR trailing stop from source omitted.
    """

    def __init__(self, config: MomentumIgnitionConfig) -> None:
        super().__init__(config)
        self._price_std = RollingStd(config.consolidation_period)
        self._roc = RateOfChange(config.roc_period)
        self._roc_mean = RollingMean(config.roc_ma_period)
        self._roc_std = RollingStd(config.roc_ma_period)
        self._trend = SimpleMovingAverage(config.trend_period)

    def _register_indicators(self) -> None:
        bt = self.port_config.bar_type
        self.register_indicator_for_bars(bt, self._roc)
        self.register_indicator_for_bars(bt, self._trend)

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        close = bar.close.as_double()
        self._price_std.update(close)
        roc = self._roc.value
        self._roc_mean.update(roc)
        self._roc_std.update(roc)

        if not self._price_std.initialized or not self._roc_std.initialized:
            return

        cfg = self.config
        consolidating = (self._price_std.value / close) < cfg.consolidation_threshold
        uptrend = close > self._trend.value
        upper = self._roc_mean.value + cfg.roc_breakout_std * self._roc_std.value

        iid = self.port_config.instrument_id
        if self.portfolio.is_net_long(iid):
            if roc < self._roc_mean.value:
                self.exit_long()
        elif consolidating and uptrend and roc > upper:
            self.enter_long()

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        return False
