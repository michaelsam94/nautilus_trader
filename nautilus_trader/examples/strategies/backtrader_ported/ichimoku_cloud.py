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

"""Port of ali-azary ``IchimokuCloudStrategy`` (long only)."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.indicators import IchimokuCloud
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import CloseHistory


class IchimokuCloudBreakoutConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``IchimokuCloudBreakout``."""

    tenkan_period: PositiveInt = 7
    kijun_period: PositiveInt = 14
    senkou_period: PositiveInt = 30
    displacement: PositiveInt = 14
    trail_percent: PositiveFloat = 0.02
    historical_bars_days: PositiveInt = 120


class IchimokuCloudBreakout(FreqtradeLongOnlyStrategy):
    """
    Ichimoku cloud breakout with TK cross and chikou confirmation (long only).

    Distinct from jesse ``SimpleBollinger`` (BB + cloud filter). Source uses
    trailing stop; here exit when close falls below trailing stop level.
    """

    def __init__(self, config: IchimokuCloudBreakoutConfig) -> None:
        super().__init__(config)
        self._ichimoku = IchimokuCloud(
            config.tenkan_period,
            config.kijun_period,
            config.senkou_period,
            config.displacement,
        )
        self._highs = CloseHistory(config.displacement + 2)
        self._trail_stop: float | None = None

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._ichimoku)

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        close = bar.close.as_double()
        high = bar.high.as_double()
        self._highs.update(high)
        iid = self.port_config.instrument_id
        cloud_top = max(self._ichimoku.senkou_span_a, self._ichimoku.senkou_span_b)
        lag_high = self._highs.shifted(self.config.displacement)

        if self.portfolio.is_net_long(iid):
            trail = high * (1.0 - self.config.trail_percent)
            if self._trail_stop is None or trail > self._trail_stop:
                self._trail_stop = trail
            if self._trail_stop is not None and close <= self._trail_stop:
                self.exit_long()
                self._trail_stop = None
            return

        chikou_ok = lag_high is not None and self._ichimoku.chikou_span > lag_high
        if (
            close > cloud_top
            and self._ichimoku.tenkan_sen > self._ichimoku.kijun_sen
            and chikou_ok
        ):
            self.enter_long()
            self._trail_stop = close * (1.0 - self.config.trail_percent)

    def check_entry(self, bar: Bar) -> bool:
        return False

    def check_exit(self, bar: Bar) -> bool:
        return False
