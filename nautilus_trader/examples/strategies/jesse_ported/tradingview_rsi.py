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

"""Port of jesse-ai/example-strategies ``TradingView_RSI``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_from_freqtrade


class TradingViewRsiConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``TradingViewRsi``."""

    rsi_period: PositiveInt = 5
    entry_rsi_level: PositiveFloat = 35.0
    exit_rsi_level: PositiveFloat = 75.0
    emergency_exit_level: PositiveFloat = 10.0


class TradingViewRsi(FreqtradeLongOnlyStrategy):
    """
    RSI cross above 35 entry; cross below 75 or 10 exit.

    Ported from jesse-ai/example-strategies ``TradingView_RSI``.
    Stop-loss / take-profit from Jesse omitted.
    """

    def __init__(self, config: TradingViewRsiConfig) -> None:
        super().__init__(config)
        self._rsi = RelativeStrengthIndex(config.rsi_period)
        self._entry_cross = CrossDetector()
        self._exit_cross = CrossDetector()

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._rsi)

    def check_entry(self, bar: Bar) -> bool:
        level = rsi_from_freqtrade(self.config.entry_rsi_level)
        return self._entry_cross.crossed_above(self._rsi.value, level)

    def check_exit(self, bar: Bar) -> bool:
        cfg = self.config
        rsi = self._rsi.value
        exit_level = rsi_from_freqtrade(cfg.exit_rsi_level)
        emergency = rsi_from_freqtrade(cfg.emergency_exit_level)
        return (
            self._exit_cross.crossed_below(rsi, exit_level)
            or self._exit_cross.crossed_below(rsi, emergency)
        )
