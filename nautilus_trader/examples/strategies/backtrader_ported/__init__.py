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

"""ali-azary Backtrader strategy ports for Nautilus Trader."""

from nautilus_trader.examples.strategies.backtrader_ported.catalog import BACKTRADER_STRATEGY_CATALOG
from nautilus_trader.examples.strategies.backtrader_ported.ichimoku_cloud import IchimokuCloudBreakout
from nautilus_trader.examples.strategies.backtrader_ported.ichimoku_cloud import IchimokuCloudBreakoutConfig
from nautilus_trader.examples.strategies.backtrader_ported.keltner_breakout import KeltnerBreakout
from nautilus_trader.examples.strategies.backtrader_ported.keltner_breakout import KeltnerBreakoutConfig
from nautilus_trader.examples.strategies.backtrader_ported.keltner_rsi_breakout import KeltnerRsiBreakout
from nautilus_trader.examples.strategies.backtrader_ported.keltner_rsi_breakout import KeltnerRsiBreakoutConfig
from nautilus_trader.examples.strategies.backtrader_ported.ml_enhanced_adx import MlEnhancedAdx
from nautilus_trader.examples.strategies.backtrader_ported.ml_enhanced_adx import MlEnhancedAdxConfig
from nautilus_trader.examples.strategies.backtrader_ported.momentum_ignition import MomentumIgnition
from nautilus_trader.examples.strategies.backtrader_ported.momentum_ignition import MomentumIgnitionConfig
from nautilus_trader.examples.strategies.backtrader_ported.obv_market_regime_breakout import ObvMarketRegimeBreakout
from nautilus_trader.examples.strategies.backtrader_ported.obv_market_regime_breakout import ObvMarketRegimeBreakoutConfig
from nautilus_trader.examples.strategies.backtrader_ported.obv_momentum import ObvMomentum
from nautilus_trader.examples.strategies.backtrader_ported.obv_momentum import ObvMomentumConfig
from nautilus_trader.examples.strategies.backtrader_ported.ou_mean_reversion import OuMeanReversion
from nautilus_trader.examples.strategies.backtrader_ported.ou_mean_reversion import OuMeanReversionConfig
from nautilus_trader.examples.strategies.backtrader_ported.quantile_channel import QuantileChannelBreakout
from nautilus_trader.examples.strategies.backtrader_ported.quantile_channel import QuantileChannelBreakoutConfig
from nautilus_trader.examples.strategies.backtrader_ported.regime_filtered_trend import RegimeFilteredTrend
from nautilus_trader.examples.strategies.backtrader_ported.regime_filtered_trend import RegimeFilteredTrendConfig
from nautilus_trader.examples.strategies.backtrader_ported.relative_momentum_accel import RelativeMomentumAccel
from nautilus_trader.examples.strategies.backtrader_ported.relative_momentum_accel import RelativeMomentumAccelConfig


__all__ = [
    "BACKTRADER_STRATEGY_CATALOG",
    "IchimokuCloudBreakout",
    "IchimokuCloudBreakoutConfig",
    "KeltnerBreakout",
    "KeltnerBreakoutConfig",
    "KeltnerRsiBreakout",
    "KeltnerRsiBreakoutConfig",
    "MlEnhancedAdx",
    "MlEnhancedAdxConfig",
    "MomentumIgnition",
    "MomentumIgnitionConfig",
    "ObvMarketRegimeBreakout",
    "ObvMarketRegimeBreakoutConfig",
    "ObvMomentum",
    "ObvMomentumConfig",
    "OuMeanReversion",
    "OuMeanReversionConfig",
    "QuantileChannelBreakout",
    "QuantileChannelBreakoutConfig",
    "RegimeFilteredTrend",
    "RegimeFilteredTrendConfig",
    "RelativeMomentumAccel",
    "RelativeMomentumAccelConfig",
]
