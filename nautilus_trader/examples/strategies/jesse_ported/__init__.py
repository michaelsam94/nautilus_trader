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

"""Jesse example-strategy ports for Nautilus Trader."""

from nautilus_trader.examples.strategies.jesse_ported.catalog import JESSE_STRATEGY_CATALOG
from nautilus_trader.examples.strategies.jesse_ported.donchian_sma200 import DonchianSma200
from nautilus_trader.examples.strategies.jesse_ported.donchian_sma200 import DonchianSma200Config
from nautilus_trader.examples.strategies.jesse_ported.ifr2 import Ifr2
from nautilus_trader.examples.strategies.jesse_ported.ifr2 import Ifr2Config
from nautilus_trader.examples.strategies.jesse_ported.indicators import KDJ
from nautilus_trader.examples.strategies.jesse_ported.kdj import Kdj
from nautilus_trader.examples.strategies.jesse_ported.kdj import KdjConfig
from nautilus_trader.examples.strategies.jesse_ported.magen_fixed import MaGenFixed
from nautilus_trader.examples.strategies.jesse_ported.magen_fixed import MaGenFixedConfig
from nautilus_trader.examples.strategies.jesse_ported.macd_ema import MacdEma
from nautilus_trader.examples.strategies.jesse_ported.macd_ema import MacdEmaConfig
from nautilus_trader.examples.strategies.jesse_ported.rsi2 import Rsi2
from nautilus_trader.examples.strategies.jesse_ported.rsi2 import Rsi2Config
from nautilus_trader.examples.strategies.jesse_ported.simple_bollinger import SimpleBollingerIchimoku
from nautilus_trader.examples.strategies.jesse_ported.simple_bollinger import SimpleBollingerIchimokuConfig
from nautilus_trader.examples.strategies.jesse_ported.tradingview_rsi import TradingViewRsi
from nautilus_trader.examples.strategies.jesse_ported.tradingview_rsi import TradingViewRsiConfig
from nautilus_trader.examples.strategies.jesse_ported.turtle_rules import TurtleRulesLong
from nautilus_trader.examples.strategies.jesse_ported.turtle_rules import TurtleRulesLongConfig


__all__ = [
    "DonchianSma200",
    "DonchianSma200Config",
    "Ifr2",
    "Ifr2Config",
    "JESSE_STRATEGY_CATALOG",
    "KDJ",
    "Kdj",
    "KdjConfig",
    "MaGenFixed",
    "MaGenFixedConfig",
    "MacdEma",
    "MacdEmaConfig",
    "Rsi2",
    "Rsi2Config",
    "SimpleBollingerIchimoku",
    "SimpleBollingerIchimokuConfig",
    "TradingViewRsi",
    "TradingViewRsiConfig",
    "TurtleRulesLong",
    "TurtleRulesLongConfig",
]
