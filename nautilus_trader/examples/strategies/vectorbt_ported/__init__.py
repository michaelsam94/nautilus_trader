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

"""vectorbt-backtesting-skills template ports for Nautilus Trader."""

from nautilus_trader.examples.strategies.vectorbt_ported.buy_hold import BuyHoldBenchmark
from nautilus_trader.examples.strategies.vectorbt_ported.buy_hold import BuyHoldBenchmarkConfig
from nautilus_trader.examples.strategies.vectorbt_ported.catalog import VECTORBT_STRATEGY_CATALOG
from nautilus_trader.examples.strategies.vectorbt_ported.donchian_breakout import DonchianBreakout
from nautilus_trader.examples.strategies.vectorbt_ported.donchian_breakout import DonchianBreakoutConfig
from nautilus_trader.examples.strategies.vectorbt_ported.double_momentum import DoubleMomentum
from nautilus_trader.examples.strategies.vectorbt_ported.double_momentum import DoubleMomentumConfig
from nautilus_trader.examples.strategies.vectorbt_ported.dual_momentum_etfs import DualMomentumEtfRotation
from nautilus_trader.examples.strategies.vectorbt_ported.dual_momentum_etfs import DualMomentumEtfRotationConfig
from nautilus_trader.examples.strategies.vectorbt_ported.dual_momentum_rotation import DualMomentumRotation
from nautilus_trader.examples.strategies.vectorbt_ported.dual_momentum_rotation import DualMomentumRotationConfig
from nautilus_trader.examples.strategies.vectorbt_ported.indicators import SDA2Bands
from nautilus_trader.examples.strategies.vectorbt_ported.rsi_accumulation import RsiAccumulation
from nautilus_trader.examples.strategies.vectorbt_ported.rsi_accumulation import RsiAccumulationConfig
from nautilus_trader.examples.strategies.vectorbt_ported.rsi_threshold import RsiThreshold
from nautilus_trader.examples.strategies.vectorbt_ported.rsi_threshold import RsiThresholdConfig
from nautilus_trader.examples.strategies.vectorbt_ported.sda2_trend import Sda2Trend
from nautilus_trader.examples.strategies.vectorbt_ported.sda2_trend import Sda2TrendConfig
from nautilus_trader.examples.strategies.vectorbt_ported.supertrend import SupertrendCross
from nautilus_trader.examples.strategies.vectorbt_ported.supertrend import SupertrendCrossConfig


__all__ = [
    "BuyHoldBenchmark",
    "BuyHoldBenchmarkConfig",
    "DonchianBreakout",
    "DonchianBreakoutConfig",
    "DoubleMomentum",
    "DoubleMomentumConfig",
    "DualMomentumEtfRotation",
    "DualMomentumEtfRotationConfig",
    "DualMomentumRotation",
    "DualMomentumRotationConfig",
    "RsiAccumulation",
    "RsiAccumulationConfig",
    "RsiThreshold",
    "RsiThresholdConfig",
    "SDA2Bands",
    "Sda2Trend",
    "Sda2TrendConfig",
    "SupertrendCross",
    "SupertrendCrossConfig",
    "VECTORBT_STRATEGY_CATALOG",
]
