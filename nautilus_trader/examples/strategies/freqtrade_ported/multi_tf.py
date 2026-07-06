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

"""Port of Freqtrade ``multi_tf`` (simplified informative RSI demo)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_from_freqtrade


class MultiTfConfig(FreqtradePortConfig, frozen=True):
    """
    Configuration for ``MultiTf``.

    Map informative bar types to upstream columns (30m/1h pair RSI, BTC 1h, etc.).
    """

    rsi_30m_bar_type: BarType
    rsi_1h_bar_type: BarType
    btc_rsi_1h_bar_type: BarType | None = None
    eth_btc_rsi_1h_bar_type: BarType | None = None
    primary_rsi_entry: PositiveFloat = 30.0
    primary_rsi_exit: PositiveFloat = 70.0


class MultiTf(FreqtradeLongOnlyStrategy):
    """
    Multi-timeframe RSI demo (ported from Freqtrade multi_tf).

  Partial: optional BTC/ETH informative pairs omitted when bar types are None.
    """

    def __init__(self, config: MultiTfConfig) -> None:
        super().__init__(config)
        self._rsi = RelativeStrengthIndex(14)
        self._rsi_30m = RelativeStrengthIndex(14)
        self._rsi_1h = RelativeStrengthIndex(14)
        self._btc_rsi = RelativeStrengthIndex(14)
        self._eth_btc_rsi = RelativeStrengthIndex(14)
        self._btc_rsi_fast = RelativeStrengthIndex(4)
        self._btc_rsi_super = RelativeStrengthIndex(2)

    def _register_indicators(self) -> None:
        primary = self.port_config.bar_type
        self.register_indicator_for_bars(primary, self._rsi)
        cfg = self.config
        self.register_indicator_for_bars(cfg.rsi_30m_bar_type, self._rsi_30m)
        self.register_indicator_for_bars(cfg.rsi_1h_bar_type, self._rsi_1h)
        if cfg.btc_rsi_1h_bar_type is not None:
            bt = cfg.btc_rsi_1h_bar_type
            self.register_indicator_for_bars(bt, self._btc_rsi)
            self.register_indicator_for_bars(bt, self._btc_rsi_fast)
            self.register_indicator_for_bars(bt, self._btc_rsi_super)
        if cfg.eth_btc_rsi_1h_bar_type is not None:
            self.register_indicator_for_bars(cfg.eth_btc_rsi_1h_bar_type, self._eth_btc_rsi)

    def check_entry(self, bar: Bar) -> bool:
        rsi = self._rsi.value
        rsi_1h = self._rsi_1h.value
        entry = rsi_from_freqtrade(self.config.primary_rsi_entry)
        if rsi >= entry or rsi >= rsi_1h:
            return False
        if self._rsi_30m.value >= rsi_from_freqtrade(40.0):
            return False
        if self._rsi_1h.value >= rsi_from_freqtrade(40.0):
            return False
        cfg = self.config
        if cfg.btc_rsi_1h_bar_type is not None:
            if self._btc_rsi.value >= rsi_from_freqtrade(35.0):
                return False
            if self._btc_rsi_fast.value >= rsi_from_freqtrade(40.0):
                return False
            if self._btc_rsi_super.value >= rsi_from_freqtrade(30.0):
                return False
        if cfg.eth_btc_rsi_1h_bar_type is not None:
            if self._eth_btc_rsi.value >= rsi_from_freqtrade(50.0):
                return False
        return self.bar_volume(bar) > 0

    def check_exit(self, bar: Bar) -> bool:
        rsi = self._rsi.value
        exit_thr = rsi_from_freqtrade(self.config.primary_rsi_exit)
        return rsi > exit_thr and rsi >= self._rsi_1h.value and self.bar_volume(bar) > 0
