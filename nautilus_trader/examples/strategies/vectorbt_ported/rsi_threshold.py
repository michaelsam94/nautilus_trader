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

"""Port of marketcalls/vectorbt-backtesting-skills RSI template."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CrossDetector
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import rsi_from_freqtrade


class RsiThresholdConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``RsiThreshold``."""

    rsi_period: PositiveInt = 14
    oversold: PositiveFloat = 30.0
    overbought: PositiveFloat = 70.0


class RsiThreshold(FreqtradeLongOnlyStrategy):
    """
    RSI cross into oversold entry; cross into overbought exit.

    Ported from vectorbt-expert ``assets/rsi/backtest.py``.
    Distinct from ``BbandRsi`` (no Bollinger filter).
    """

    def __init__(self, config: RsiThresholdConfig) -> None:
        super().__init__(config)
        self._rsi = RelativeStrengthIndex(config.rsi_period)
        self._entry_cross = CrossDetector()
        self._exit_cross = CrossDetector()
        self._prev_rsi: float | None = None

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._rsi)

    def check_entry(self, bar: Bar) -> bool:
        cfg = self.config
        rsi = self._rsi.value
        oversold = rsi_from_freqtrade(cfg.oversold)
        if self._prev_rsi is None:
            self._prev_rsi = rsi
            return False
        entry = self._prev_rsi >= oversold and rsi < oversold
        self._prev_rsi = rsi
        return entry

    def check_exit(self, bar: Bar) -> bool:
        overbought = rsi_from_freqtrade(self.config.overbought)
        return self._exit_cross.crossed_above(self._rsi.value, overbought)
