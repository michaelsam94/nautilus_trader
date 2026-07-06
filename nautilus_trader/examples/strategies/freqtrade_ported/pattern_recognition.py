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

"""Port of Freqtrade ``PatternRecognition``."""

from typing import Literal

from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import HammerPattern
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import HighWavePattern


PatternName = Literal["CDLHAMMER", "CDLHIGHWAVE"]


class PatternRecognitionConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``PatternRecognition`` (hyperopt default)."""

    pattern: PatternName = "CDLHIGHWAVE"
    pattern_value: float = -100.0


class PatternRecognition(FreqtradeLongOnlyStrategy):
    """
    Candlestick pattern entry (ported from Freqtrade PatternRecognition).

    Only ``CDLHAMMER`` and ``CDLHIGHWAVE`` are implemented; other TALib patterns omitted.
    """

    def __init__(self, config: PatternRecognitionConfig) -> None:
        super().__init__(config)
        self._hammer = HammerPattern()
        self._highwave = HighWavePattern()

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        if self.config.pattern == "CDLHAMMER":
            self.register_indicator_for_bars(bar_type, self._hammer)
        elif self.config.pattern == "CDLHIGHWAVE":
            self.register_indicator_for_bars(bar_type, self._highwave)

    def check_entry(self, bar: Bar) -> bool:
        if self.config.pattern == "CDLHAMMER":
            return self._hammer.value == self.config.pattern_value
        if self.config.pattern == "CDLHIGHWAVE":
            return self._highwave.value == self.config.pattern_value
        return False

    def check_exit(self, bar: Bar) -> bool:
        return False
