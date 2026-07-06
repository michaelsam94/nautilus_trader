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

"""
Fixed-parameter port of jesse-ai/example-strategies ``MAGen``.

The Jesse source is a genetic-algorithm strategy generator with tunable MA types,
sources, and ADX/ATR hyperparameters. This module freezes the default
hyperparameter values as a runnable long-only ruleset.
"""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import AverageTrueRange
from nautilus_trader.indicators import ExponentialMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import AverageDirectionalIndex


class MaGenFixedConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``MaGenFixed`` (Jesse MAGen default hyperparameters)."""

    ma_fast_period: PositiveInt = 5
    ma_slow_period: PositiveInt = 20
    adx_period: PositiveInt = 8
    adx_entry: PositiveFloat = 13.0
    adx_exit: PositiveFloat = 15.0
    atr_period: PositiveInt = 32
    stop_loss_atr_rate: PositiveFloat = 2.0
    take_profit_atr_rate: PositiveFloat = 5.0
    historical_bars_days: PositiveInt = 120


class MaGenFixed(FreqtradeLongOnlyStrategy):
    """
    MA crossover with ADX filter and ATR stop/take-profit (long only).

    Ported from jesse-ai/example-strategies ``MAGen`` with genetic search omitted;
    uses default ``hyperparameters()`` values from the Jesse source.
    """

    def __init__(self, config: MaGenFixedConfig) -> None:
        super().__init__(config)
        self._ma_fast = ExponentialMovingAverage(config.ma_fast_period)
        self._ma_slow = ExponentialMovingAverage(config.ma_slow_period)
        self._adx = AverageDirectionalIndex(config.adx_period)
        self._atr = AverageTrueRange(config.atr_period)
        self._cross = CrossDetector()
        self._entry_price: float | None = None

    def _register_indicators(self) -> None:
        bt = self.port_config.bar_type
        for ind in (self._ma_fast, self._ma_slow, self._adx, self._atr):
            self.register_indicator_for_bars(bt, ind)

    def check_entry(self, bar: Bar) -> bool:
        crossed = self._cross.crossed_above(self._ma_fast.value, self._ma_slow.value)
        return crossed and self._adx.adx > self.config.adx_entry

    def check_exit(self, bar: Bar) -> bool:
        return (
            self._ma_fast.value < self._ma_slow.value
            and self._adx.adx < self.config.adx_exit
        )

    def check_custom_stoploss(self, bar: Bar) -> bool:
        if self._entry_price is None or self._atr.value <= 0:
            return False
        close = bar.close.as_double()
        stop = self._entry_price - self._atr.value * self.config.stop_loss_atr_rate
        target = self._entry_price + self._atr.value * self.config.take_profit_atr_rate
        return close <= stop or close >= target

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        iid = self.port_config.instrument_id
        if self.portfolio.is_net_long(iid):
            if self.check_custom_stoploss(bar) or self.check_exit(bar):
                self.exit_long()
                self._entry_price = None
            return

        if self.check_entry(bar) and self.portfolio.is_flat(iid):
            self.enter_long()
            self._entry_price = bar.close.as_double()
