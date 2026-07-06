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

"""Port of ali-azary ``RelativeMomentumAccel`` (long only)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.backtrader_ported.indicators import ThrustOscillator
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import RollingMean
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import RollingStd


class RelativeMomentumAccelConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``RelativeMomentumAccel``."""

    kama_period: PositiveInt = 30
    fast_ema_period: PositiveInt = 7
    thrust_bb_period: PositiveInt = 7
    thrust_bb_devfactor: PositiveFloat = 1.0


class RelativeMomentumAccel(FreqtradeLongOnlyStrategy):
    """
    Thrust oscillator Bollinger breakout entry (long only).

    Ported from ali-azary ``RelativeMomentumAccel``.
    ATR trailing stop from source replaced by mid-band mean reversion exit.
    """

    def __init__(self, config: RelativeMomentumAccelConfig) -> None:
        super().__init__(config)
        self._thrust = ThrustOscillator(config.kama_period, config.fast_ema_period)
        self._thrust_std = RollingStd(config.thrust_bb_period)
        self._thrust_avg = RollingMean(config.thrust_bb_period)

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._thrust)

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        thrust = self._thrust.value
        self._thrust_std.update(thrust)
        self._thrust_avg.update(thrust)
        if not self._thrust_std.initialized or not self._thrust_avg.initialized:
            return

        mean = self._thrust_avg.value
        upper = mean + self.config.thrust_bb_devfactor * self._thrust_std.value

        iid = self.port_config.instrument_id
        if self.portfolio.is_net_long(iid):
            if thrust < mean:
                self.exit_long()
        elif thrust > upper:
            self.enter_long()

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        return False
