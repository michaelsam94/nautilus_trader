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

"""Port of ali-azary ``OUMeanReversionStrategy`` (long only)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.backtrader_ported.indicators import OUZScore
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class OuMeanReversionConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``OuMeanReversion``."""

    lookback: PositiveInt = 30
    sma_period: PositiveInt = 30
    entry_threshold: PositiveFloat = 1.0
    exit_threshold: PositiveFloat = 0.0
    historical_bars_days: PositiveInt = 60


class OuMeanReversion(FreqtradeLongOnlyStrategy):
    """
    Long when OU z-score below -entry and price above SMA (long-only subset).

    Ported from ali-azary ``OUMeanReversionStrategy``; short leg omitted.
    """

    def __init__(self, config: OuMeanReversionConfig) -> None:
        super().__init__(config)
        self._ou = OUZScore(config.lookback)
        self._sma = SimpleMovingAverage(config.sma_period)

    def _register_indicators(self) -> None:
        bt = self.port_config.bar_type
        self.register_indicator_for_bars(bt, self._ou)
        self.register_indicator_for_bars(bt, self._sma)

    def check_entry(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        return (
            self._ou.z_score < -self.config.entry_threshold
            and close > self._sma.value
        )

    def check_exit(self, bar: Bar) -> bool:
        return self._ou.z_score > -self.config.exit_threshold
