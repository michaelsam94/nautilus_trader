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

"""Port of Freqtrade ``SwingHighToSky`` (CCI + RSI thresholds)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import CommodityChannelIndex
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_from_freqtrade


class SwingHighToSkyConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``SwingHighToSky``."""

    buy_cci_period: PositiveInt = 72
    buy_cci_threshold: float = -175.0
    buy_rsi_period: PositiveInt = 36
    buy_rsi_threshold: PositiveFloat = 90.0
    sell_cci_period: PositiveInt = 66
    sell_cci_threshold: float = -106.0
    sell_rsi_period: PositiveInt = 45
    sell_rsi_threshold: PositiveFloat = 88.0


class SwingHighToSky(FreqtradeLongOnlyStrategy):
    """
    CCI and RSI threshold entry/exit (hyperopt defaults).

    Ported from ``user_data/strategies/SwingHighToSky.py``.
    """

    def __init__(self, config: SwingHighToSkyConfig) -> None:
        super().__init__(config)
        self._buy_cci = CommodityChannelIndex(config.buy_cci_period)
        self._sell_cci = CommodityChannelIndex(config.sell_cci_period)
        self._buy_rsi = RelativeStrengthIndex(config.buy_rsi_period)
        self._sell_rsi = RelativeStrengthIndex(config.sell_rsi_period)

    def _register_indicators(self) -> None:
        bt = self.port_config.bar_type
        for ind in (self._buy_cci, self._sell_cci, self._buy_rsi, self._sell_rsi):
            self.register_indicator_for_bars(bt, ind)

    def check_entry(self, bar: Bar) -> bool:
        cfg = self.config
        return (
            self._buy_cci.value < cfg.buy_cci_threshold
            and self._buy_rsi.value < rsi_from_freqtrade(cfg.buy_rsi_threshold)
        )

    def check_exit(self, bar: Bar) -> bool:
        cfg = self.config
        return (
            self._sell_cci.value > cfg.sell_cci_threshold
            and self._sell_rsi.value > rsi_from_freqtrade(cfg.sell_rsi_threshold)
        )
