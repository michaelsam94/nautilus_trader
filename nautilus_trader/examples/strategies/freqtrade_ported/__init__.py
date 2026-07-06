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

"""Freqtrade strategy ports for Nautilus Trader."""

from nautilus_trader.examples.strategies.freqtrade_ported.adx_momentum import AdxMomentum
from nautilus_trader.examples.strategies.freqtrade_ported.adx_momentum import AdxMomentumConfig
from nautilus_trader.examples.strategies.freqtrade_ported.adx_smas import AdxSmas
from nautilus_trader.examples.strategies.freqtrade_ported.adx_smas import AdxSmasConfig
from nautilus_trader.examples.strategies.freqtrade_ported.average_strategy import AverageStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.average_strategy import AverageStrategyConfig
from nautilus_trader.examples.strategies.freqtrade_ported.awesome_macd import AwesomeMacd
from nautilus_trader.examples.strategies.freqtrade_ported.awesome_macd import AwesomeMacdConfig
from nautilus_trader.examples.strategies.freqtrade_ported.bandtastic import Bandtastic
from nautilus_trader.examples.strategies.freqtrade_ported.bandtastic import BandtasticConfig
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.bband_rsi import BbandRsi
from nautilus_trader.examples.strategies.freqtrade_ported.bband_rsi import BbandRsiConfig
from nautilus_trader.examples.strategies.freqtrade_ported.catalog import FREQTRADE_STRATEGY_CATALOG
from nautilus_trader.examples.strategies.freqtrade_ported.catalog import PortStatus
from nautilus_trader.examples.strategies.freqtrade_ported.cmc_winner import CmcWinner
from nautilus_trader.examples.strategies.freqtrade_ported.cmc_winner import CmcWinnerConfig
from nautilus_trader.examples.strategies.freqtrade_ported.diamond import Diamond
from nautilus_trader.examples.strategies.freqtrade_ported.diamond import DiamondConfig
from nautilus_trader.examples.strategies.freqtrade_ported.does_nothing import DoesNothing
from nautilus_trader.examples.strategies.freqtrade_ported.does_nothing import DoesNothingConfig
from nautilus_trader.examples.strategies.freqtrade_ported.hlhb import Hlhb
from nautilus_trader.examples.strategies.freqtrade_ported.hlhb import HlhbConfig
from nautilus_trader.examples.strategies.freqtrade_ported.low_bb import LowBb
from nautilus_trader.examples.strategies.freqtrade_ported.low_bb import LowBbConfig
from nautilus_trader.examples.strategies.freqtrade_ported.macd_strategy import MacdStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.macd_strategy import MacdStrategyConfig
from nautilus_trader.examples.strategies.freqtrade_ported.macd_strategy_crossed import MacdStrategyCrossed
from nautilus_trader.examples.strategies.freqtrade_ported.macd_strategy_crossed import MacdStrategyCrossedConfig
from nautilus_trader.examples.strategies.freqtrade_ported.scalp import Scalp
from nautilus_trader.examples.strategies.freqtrade_ported.scalp import ScalpConfig
from nautilus_trader.examples.strategies.freqtrade_ported.simple_strategy import Simple
from nautilus_trader.examples.strategies.freqtrade_ported.simple_strategy import SimpleConfig
from nautilus_trader.examples.strategies.freqtrade_ported.strategy001 import Strategy001
from nautilus_trader.examples.strategies.freqtrade_ported.strategy001 import Strategy001Config
from nautilus_trader.examples.strategies.freqtrade_ported.technical_example import TechnicalExample
from nautilus_trader.examples.strategies.freqtrade_ported.technical_example import TechnicalExampleConfig
from nautilus_trader.examples.strategies.freqtrade_ported.universal_macd import UniversalMacd
from nautilus_trader.examples.strategies.freqtrade_ported.universal_macd import UniversalMacdConfig


__all__ = [
    "AdxMomentum",
    "AdxMomentumConfig",
    "AdxSmas",
    "AdxSmasConfig",
    "AverageStrategy",
    "AverageStrategyConfig",
    "AwesomeMacd",
    "AwesomeMacdConfig",
    "Bandtastic",
    "BandtasticConfig",
    "BbandRsi",
    "BbandRsiConfig",
    "CmcWinner",
    "CmcWinnerConfig",
    "Diamond",
    "DiamondConfig",
    "DoesNothing",
    "DoesNothingConfig",
    "FREQTRADE_STRATEGY_CATALOG",
    "FreqtradeLongOnlyStrategy",
    "FreqtradePortConfig",
    "Hlhb",
    "HlhbConfig",
    "LowBb",
    "LowBbConfig",
    "MacdStrategy",
    "MacdStrategyConfig",
    "MacdStrategyCrossed",
    "MacdStrategyCrossedConfig",
    "PortStatus",
    "Scalp",
    "ScalpConfig",
    "Simple",
    "SimpleConfig",
    "Strategy001",
    "Strategy001Config",
    "TechnicalExample",
    "TechnicalExampleConfig",
    "UniversalMacd",
    "UniversalMacdConfig",
]
