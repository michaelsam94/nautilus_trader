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

"""Port of Freqtrade ``FixedRiskRewardLoss``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.indicators import AverageTrueRange
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class FixedRiskRewardLossConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``FixedRiskRewardLoss``."""

    atr_multiplier: PositiveFloat = 2.0
    risk_reward_ratio: PositiveFloat = 3.5
    break_even_risk_multiple: PositiveFloat = 1.0


class FixedRiskRewardLoss(FreqtradeLongOnlyStrategy):
    """
    Fixed R:R custom stoploss example (ported from Freqtrade FixedRiskRewardLoss).

    Always enters when flat; manages stop via ATR-based levels in ``on_bar``.
    """

    def __init__(self, config: FixedRiskRewardLossConfig) -> None:
        super().__init__(config)
        self._atr = AverageTrueRange(14)
        self._stop_price: float | None = None
        self._take_profit_price: float | None = None
        self._break_even_price: float | None = None

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._atr)

    def check_entry(self, bar: Bar) -> bool:
        return True

    def check_exit(self, bar: Bar) -> bool:
        return False

    def enter_long(self) -> None:
        super().enter_long()
        self._stop_price = None
        self._take_profit_price = None
        self._break_even_price = None

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type != self.port_config.bar_type:
            return
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        iid = self.port_config.instrument_id
        close = bar.close.as_double()

        if self.portfolio.is_net_long(iid):
            position = self.portfolio.position(iid)
            if position is None:
                return
            entry = position.avg_px_open.as_double()
            if self._stop_price is None and self._atr.initialized:
                self._stop_price = close - self.config.atr_multiplier * self._atr.value
                risk = entry - self._stop_price
                self._take_profit_price = entry + risk * self.config.risk_reward_ratio
                self._break_even_price = entry + risk * self.config.break_even_risk_multiple

            if self._stop_price is not None and close <= self._stop_price:
                self.exit_long()
                return
            if self._take_profit_price is not None and close >= self._take_profit_price:
                self.exit_long()
                return
            if (
                self._break_even_price is not None
                and close >= self._break_even_price
                and self._stop_price is not None
                and self._stop_price < entry
            ):
                self._stop_price = entry
            return

        if self.check_entry(bar) and self.portfolio.is_flat(iid):
            self.enter_long()
