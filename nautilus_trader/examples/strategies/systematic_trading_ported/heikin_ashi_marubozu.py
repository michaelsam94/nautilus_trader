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

"""Port of je-suis-tm/quant-trading Heikin-Ashi marubozu rules."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import HeikinAshi


class HeikinAshiMarubozuConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``HeikinAshiMarubozu``."""

    max_stacked_entries: PositiveInt = 1


class HeikinAshiMarubozu(FreqtradeLongOnlyStrategy):
    """
    Heikin-Ashi momentum marubozu entry/exit (distinct from Freqtrade Strategy001).

    Source: je-suis-tm/quant-trading ``Heikin-Ashi backtest.py``.
    Dedup: Strategy001 uses HA + EMA crosses; this uses HA marubozu body rules.
    """

    def __init__(self, config: HeikinAshiMarubozuConfig) -> None:
        super().__init__(config)
        self._ha = HeikinAshi()
        self._prev_body: float | None = None
        self._prev_ha_bearish: bool = False
        self._stacked: int = 0

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._ha)

    def _body_size(self) -> float:
        return abs(self._ha.open - self._ha.close)

    def check_entry(self, bar: Bar) -> bool:
        if self._prev_body is None:
            return False
        body = self._body_size()
        entry = (
            self._ha.open > self._ha.close
            and self._ha.open == self._ha.high
            and body > self._prev_body
            and self._prev_ha_bearish
        )
        if entry and self._stacked < self.config.max_stacked_entries:
            self._stacked += 1
            return True
        return False

    def check_exit(self, bar: Bar) -> bool:
        exit_signal = (
            self._ha.open < self._ha.close
            and self._ha.open == self._ha.low
        )
        if exit_signal:
            self._stacked = 0
        return exit_signal

    def on_bar(self, bar: Bar) -> None:
        if self.indicators_initialized():
            self._prev_body = self._body_size()
            self._prev_ha_bearish = self._ha.open > self._ha.close
        super().on_bar(bar)
