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

"""Port of jesse-ai/example-strategies ``SimpleBollinger`` (Ichimoku filter)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import BollingerBands
from nautilus_trader.indicators import IchimokuCloud
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class SimpleBollingerIchimokuConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``SimpleBollingerIchimoku``."""

    bb_period: PositiveInt = 20
    bb_std: PositiveFloat = 2.0
    historical_bars_days: PositiveInt = 120


class SimpleBollingerIchimoku(FreqtradeLongOnlyStrategy):
    """
    Bollinger upper-band breakout above Ichimoku cloud; exit below middle band.

    Ported from jesse-ai/example-strategies ``SimpleBollinger``.
  Uses typical price (HLC/3) for Bollinger bands (Jesse source uses HL2).
    """

    def __init__(self, config: SimpleBollingerIchimokuConfig) -> None:
        super().__init__(config)
        self._bb = BollingerBands(config.bb_period, config.bb_std)
        self._ichimoku = IchimokuCloud()

    def _register_indicators(self) -> None:
        bt = self.port_config.bar_type
        self.register_indicator_for_bars(bt, self._bb)
        self.register_indicator_for_bars(bt, self._ichimoku)

    def check_entry(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        cloud_top = max(self._ichimoku.senkou_span_a, self._ichimoku.senkou_span_b)
        return (
            close > cloud_top
            and close > self._bb.upper
        )

    def check_exit(self, bar: Bar) -> bool:
        return bar.close.as_double() < self._bb.middle
