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

"""Ports from awesome-systematic-trading linked alpha repositories."""

from nautilus_trader.examples.strategies.systematic_trading_ported.bollinger_bottom_w import BollingerBottomW
from nautilus_trader.examples.strategies.systematic_trading_ported.bollinger_bottom_w import BollingerBottomWConfig
from nautilus_trader.examples.strategies.systematic_trading_ported.catalog import AST_STRATEGY_CATALOG
from nautilus_trader.examples.strategies.systematic_trading_ported.catalog import AstStatus
from nautilus_trader.examples.strategies.systematic_trading_ported.dedup import QUANT_TRADING_DEDUP
from nautilus_trader.examples.strategies.systematic_trading_ported.dual_thrust import DualThrust
from nautilus_trader.examples.strategies.systematic_trading_ported.dual_thrust import DualThrustConfig
from nautilus_trader.examples.strategies.systematic_trading_ported.heikin_ashi_marubozu import HeikinAshiMarubozu
from nautilus_trader.examples.strategies.systematic_trading_ported.heikin_ashi_marubozu import HeikinAshiMarubozuConfig
from nautilus_trader.examples.strategies.systematic_trading_ported.london_breakout import LondonBreakout
from nautilus_trader.examples.strategies.systematic_trading_ported.london_breakout import LondonBreakoutConfig
from nautilus_trader.examples.strategies.systematic_trading_ported.parabolic_sar import ParabolicSarStrategy
from nautilus_trader.examples.strategies.systematic_trading_ported.parabolic_sar import ParabolicSarStrategyConfig


__all__ = [
    "AST_STRATEGY_CATALOG",
    "AstStatus",
    "BollingerBottomW",
    "BollingerBottomWConfig",
    "DualThrust",
    "DualThrustConfig",
    "HeikinAshiMarubozu",
    "HeikinAshiMarubozuConfig",
    "LondonBreakout",
    "LondonBreakoutConfig",
    "ParabolicSarStrategy",
    "ParabolicSarStrategyConfig",
    "QUANT_TRADING_DEDUP",
]
