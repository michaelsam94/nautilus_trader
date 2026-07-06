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

"""Port of vectorbt ``buy_hold`` benchmark (single-asset buy-and-hold)."""

from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig


class BuyHoldBenchmarkConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``BuyHoldBenchmark``."""


class BuyHoldBenchmark(FreqtradeLongOnlyStrategy):
    """
    Enter long on the first bar after warm-up; hold until strategy stop.

    Minimal reference benchmark ported from vectorbt-backtesting-skills
    ``buy_hold_75_25_backtest.py`` (single-instrument subset; multi-ETF
    weights require a portfolio-level runner).
    """

    def __init__(self, config: BuyHoldBenchmarkConfig) -> None:
        super().__init__(config)
        self._entered = False

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        return False

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type != self.port_config.bar_type:
            return
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        iid = self.port_config.instrument_id
        if not self._entered and self.portfolio.is_flat(iid):
            self.enter_long()
            self._entered = True
