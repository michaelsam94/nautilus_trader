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

"""Port of vectorbt ``rsi_accumulation`` (simplified DCA on RSI slabs)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_from_freqtrade


class RsiAccumulationConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``RsiAccumulation``."""

    rsi_period: PositiveInt = 14
    rsi_buy_threshold: PositiveFloat = 68.0
    rsi_exit_threshold: PositiveFloat = 70.0
    slab_mid_threshold: PositiveFloat = 50.0
    slab_low_threshold: PositiveFloat = 30.0
    historical_bars_days: PositiveInt = 90


class RsiAccumulation(FreqtradeLongOnlyStrategy):
    """
    Scale-in when RSI below buy threshold; full exit above exit threshold.

    Ported from marketcalls ``niftybees_rsi_accumulation_backtest.py``.
    Weekly NIFTY RSI + Friday 3:15 PM schedule simplified to bar RSI slabs.
    Accumulation uses repeated ``enter_long`` while RSI remains in buy zone.
    """

    def __init__(self, config: RsiAccumulationConfig) -> None:
        super().__init__(config)
        self._rsi = RelativeStrengthIndex(config.rsi_period)

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._rsi)

    def _rsi_100(self) -> float:
        return self._rsi.value * 100.0

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        rsi = self._rsi_100()
        iid = self.port_config.instrument_id
        buy_thresh = self.config.rsi_buy_threshold
        exit_thresh = self.config.rsi_exit_threshold

        if self.portfolio.is_net_long(iid) and rsi > exit_thresh:
            self.exit_long()
            return

        if rsi >= buy_thresh:
            return

        if rsi >= self.config.slab_mid_threshold:
            if self.portfolio.is_flat(iid):
                self.enter_long()
        elif rsi >= self.config.slab_low_threshold:
            self.enter_long()
        else:
            self.enter_long()

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        return False
