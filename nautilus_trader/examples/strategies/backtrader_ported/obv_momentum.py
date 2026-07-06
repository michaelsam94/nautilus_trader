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

"""Port of ali-azary ``OBVmomentumStrategy`` (long only)."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.backtrader_ported.indicators import ObvWithSignal
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import RollingMean
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_from_freqtrade


class ObvMomentumConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``ObvMomentum``."""

    obv_ma_period: PositiveInt = 30
    rsi_period: PositiveInt = 14
    volume_ma_period: PositiveInt = 7


class ObvMomentum(FreqtradeLongOnlyStrategy):
    """
    OBV crosses above its MA with RSI and volume filters (long only).

    Ported from ali-azary ``OBVmomentumStrategy``.
    """

    def __init__(self, config: ObvMomentumConfig) -> None:
        super().__init__(config)
        self._obv = ObvWithSignal(config.obv_ma_period)
        self._rsi = RelativeStrengthIndex(config.rsi_period)
        self._volume_ma = RollingMean(config.volume_ma_period)

    def _register_indicators(self) -> None:
        bt = self.port_config.bar_type
        self.register_indicator_for_bars(bt, self._obv)
        self.register_indicator_for_bars(bt, self._rsi)

    def check_entry(self, bar: Bar) -> bool:
        return (
            self._obv.cross_up
            and self._rsi.value < rsi_from_freqtrade(70)
            and self.bar_volume(bar) > self._volume_ma.value
        )

    def check_exit(self, bar: Bar) -> bool:
        return self._obv.cross_down

    def on_bar(self, bar: Bar) -> None:
        self._volume_ma.update(self.bar_volume(bar))
        super().on_bar(bar)
