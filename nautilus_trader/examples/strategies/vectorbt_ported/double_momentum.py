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

"""Port of marketcalls/vectorbt-backtesting-skills momentum template."""

from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import RateOfChange
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import ShiftedValue


class DoubleMomentumConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``DoubleMomentum``."""

    mom_period: PositiveInt = 12


class DoubleMomentum(FreqtradeLongOnlyStrategy):
    """
    MOM > 0 and MOM-of-MOM > 0 entry; opposite exit.

    Ported from vectorbt-expert ``assets/momentum/backtest.py``.
    High-breakout fill rule simplified to bar close signal.
    """

    def __init__(self, config: DoubleMomentumConfig) -> None:
        super().__init__(config)
        self._mom = RateOfChange(config.mom_period)
        self._prev_mom = ShiftedValue()

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._mom)

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        prev_mom = self._prev_mom.update(self._mom.value)
        mom1 = None if prev_mom is None else self._mom.value - prev_mom
        iid = self.port_config.instrument_id

        if mom1 is not None:
            if self.portfolio.is_net_long(iid) and self._mom.value < 0 and mom1 < 0:
                self.exit_long()
                return
            if self.portfolio.is_flat(iid) and self._mom.value > 0 and mom1 > 0:
                self.enter_long()

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        return False
