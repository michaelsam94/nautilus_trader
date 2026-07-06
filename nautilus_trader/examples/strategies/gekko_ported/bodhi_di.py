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

"""Port of xFFFFF/Gekko-Strategies ``BodhiDI_public``."""

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import (
    AverageDirectionalIndex,
)


class BodhiDiConfig(FreqtradePortConfig, frozen=True):
    """Configuration for ``BodhiDi``. Defaults from ``BodhiDI_public.toml``."""

    di_period: PositiveInt = 14
    di_plus_threshold: PositiveFloat = 23.5
    di_minus_threshold: PositiveFloat = 23.0


class BodhiDi(FreqtradeLongOnlyStrategy):
    """
    Directional-indicator flipper: long when +DI leads and exceeds its
    threshold, flat when -DI leads and exceeds its threshold.

    Distinct from ``freqtrade_ported.adx_momentum.AdxMomentum`` — no ADX gate
    and no momentum filter, absolute DI thresholds instead.
    """

    def __init__(self, config: BodhiDiConfig) -> None:
        super().__init__(config)
        self._di = AverageDirectionalIndex(config.di_period)

    def _register_indicators(self) -> None:
        self.register_indicator_for_bars(self.port_config.bar_type, self._di)

    def check_entry(self, bar: Bar) -> bool:
        cfg = self.config
        return (
            self._di.plus_di > self._di.minus_di
            and self._di.plus_di > cfg.di_plus_threshold
        )

    def check_exit(self, bar: Bar) -> bool:
        cfg = self.config
        return (
            self._di.minus_di > self._di.plus_di
            and self._di.minus_di > cfg.di_minus_threshold
        )
