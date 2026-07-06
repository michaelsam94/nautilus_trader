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

"""Port of marketcalls/vectorbt-backtesting-skills supertrend template."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import ShiftedValue
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import SuperTrend


class SupertrendCrossConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``SupertrendCross``."""

    st_period: PositiveInt = 10
    st_multiplier: PositiveFloat = 3.0


class SupertrendCross(FreqtradeLongOnlyStrategy):
    """
    Long on close cross above SuperTrend line; exit on cross below.

    Ported from vectorbt-expert ``assets/supertrend/backtest.py``.
    Intraday session windows from source omitted.
    """

    def __init__(self, config: SupertrendCrossConfig) -> None:
        super().__init__(config)
        self._st = SuperTrend(config.st_period, config.st_multiplier)
        self._prev_line = ShiftedValue()
        self._prev_close = ShiftedValue()

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._st)

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        prev_line = self._prev_line.update(self._st.line)
        prev_close = self._prev_close.update(bar.close.as_double())
        close = bar.close.as_double()
        iid = self.port_config.instrument_id

        if prev_line is not None and prev_close is not None:
            if self.portfolio.is_net_long(iid):
                if prev_close >= prev_line and close < self._st.line:
                    self.exit_long()
                    return
            elif prev_close <= prev_line and close > self._st.line:
                self.enter_long()
                return

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        return False
