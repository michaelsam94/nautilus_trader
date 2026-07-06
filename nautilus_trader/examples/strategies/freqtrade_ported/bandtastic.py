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

"""Port of Freqtrade ``Bandtastic`` (default hyperopt parameters)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import BollingerBands
from nautilus_trader.indicators import ExponentialMovingAverage
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_from_freqtrade
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import MoneyFlowIndex


class BandtasticConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``Bandtastic`` (defaults from Freqtrade hyperopt)."""

    buy_fastema: PositiveInt = 211
    buy_slowema: PositiveInt = 250
    buy_rsi: PositiveFloat = 52.0
    buy_mfi: PositiveFloat = 30.0
    buy_rsi_enabled: bool = False
    buy_mfi_enabled: bool = False
    buy_ema_enabled: bool = False
    buy_bb_std: PositiveFloat = 1.0
    sell_fastema: PositiveInt = 7
    sell_slowema: PositiveInt = 6
    sell_rsi: PositiveFloat = 57.0
    sell_mfi: PositiveFloat = 46.0
    sell_rsi_enabled: bool = False
    sell_mfi_enabled: bool = True
    sell_ema_enabled: bool = False
    sell_bb_std: PositiveFloat = 2.0


class Bandtastic(FreqtradeLongOnlyStrategy):
    """Multi-BB + optional EMA/RSI/MFI filters (ported from Bandtastic)."""

    def __init__(self, config: BandtasticConfig) -> None:
        super().__init__(config)
        self._bb_buy = BollingerBands(20, config.buy_bb_std)
        self._bb_sell = BollingerBands(20, config.sell_bb_std)
        self._rsi = RelativeStrengthIndex(14)
        self._mfi = MoneyFlowIndex(14)
        self._buy_fast_ema = ExponentialMovingAverage(config.buy_fastema)
        self._buy_slow_ema = ExponentialMovingAverage(config.buy_slowema)
        self._sell_fast_ema = ExponentialMovingAverage(config.sell_fastema)
        self._sell_slow_ema = ExponentialMovingAverage(config.sell_slowema)

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        for ind in (
            self._bb_buy,
            self._bb_sell,
            self._rsi,
            self._mfi,
            self._buy_fast_ema,
            self._buy_slow_ema,
            self._sell_fast_ema,
            self._sell_slow_ema,
        ):
            self.register_indicator_for_bars(bar_type, ind)

    def check_entry(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        cfg = self.config
        if close > self._bb_buy.lower:
            return False
        if cfg.buy_rsi_enabled and self._rsi.value > rsi_from_freqtrade(cfg.buy_rsi):
            return False
        if cfg.buy_mfi_enabled and self._mfi.value > cfg.buy_mfi:
            return False
        if cfg.buy_ema_enabled and self._buy_fast_ema.value < self._buy_slow_ema.value:
            return False
        return True

    def check_exit(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        cfg = self.config
        if close < self._bb_sell.upper:
            return False
        if cfg.sell_rsi_enabled and self._rsi.value < rsi_from_freqtrade(cfg.sell_rsi):
            return False
        if cfg.sell_mfi_enabled and self._mfi.value < cfg.sell_mfi:
            return False
        if cfg.sell_ema_enabled and self._sell_fast_ema.value > self._sell_slow_ema.value:
            return False
        return True
