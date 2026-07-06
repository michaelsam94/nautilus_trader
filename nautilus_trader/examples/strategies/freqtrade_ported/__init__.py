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
from nautilus_trader.examples.strategies.freqtrade_ported.asdts_rockwell import AsdtsRockwell
from nautilus_trader.examples.strategies.freqtrade_ported.asdts_rockwell import AsdtsRockwellConfig
from nautilus_trader.examples.strategies.freqtrade_ported.average_strategy import AverageStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.average_strategy import AverageStrategyConfig
from nautilus_trader.examples.strategies.freqtrade_ported.awesome_macd import AwesomeMacd
from nautilus_trader.examples.strategies.freqtrade_ported.awesome_macd import AwesomeMacdConfig
from nautilus_trader.examples.strategies.freqtrade_ported.bandtastic import Bandtastic
from nautilus_trader.examples.strategies.freqtrade_ported.bandtastic import BandtasticConfig
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongShortStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.bband_rsi import BbandRsi
from nautilus_trader.examples.strategies.freqtrade_ported.bband_rsi import BbandRsiConfig
from nautilus_trader.examples.strategies.freqtrade_ported.bin_hv27 import BinHv27
from nautilus_trader.examples.strategies.freqtrade_ported.bin_hv27 import BinHv27Config
from nautilus_trader.examples.strategies.freqtrade_ported.bin_hv45 import BinHv45
from nautilus_trader.examples.strategies.freqtrade_ported.bin_hv45 import BinHv45Config
from nautilus_trader.examples.strategies.freqtrade_ported.break_even import BreakEven
from nautilus_trader.examples.strategies.freqtrade_ported.break_even import BreakEvenConfig
from nautilus_trader.examples.strategies.freqtrade_ported.catalog import FREQTRADE_STRATEGY_CATALOG
from nautilus_trader.examples.strategies.freqtrade_ported.catalog import PortStatus
from nautilus_trader.examples.strategies.freqtrade_ported.cluc_may72018 import ClucMay72018
from nautilus_trader.examples.strategies.freqtrade_ported.cluc_may72018 import ClucMay72018Config
from nautilus_trader.examples.strategies.freqtrade_ported.cci_strategy import CciStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.cci_strategy import CciStrategyConfig
from nautilus_trader.examples.strategies.freqtrade_ported.cofi_bit import CofiBit
from nautilus_trader.examples.strategies.freqtrade_ported.cofi_bit import CofiBitConfig
from nautilus_trader.examples.strategies.freqtrade_ported.combined_bin_h_cluc import CombinedBinHAndCluc
from nautilus_trader.examples.strategies.freqtrade_ported.combined_bin_h_cluc import CombinedBinHAndClucConfig
from nautilus_trader.examples.strategies.freqtrade_ported.cmc_winner import CmcWinner
from nautilus_trader.examples.strategies.freqtrade_ported.cmc_winner import CmcWinnerConfig
from nautilus_trader.examples.strategies.freqtrade_ported.custom_stoploss_psar import CustomStoplossWithPsar
from nautilus_trader.examples.strategies.freqtrade_ported.custom_stoploss_psar import CustomStoplossWithPsarConfig
from nautilus_trader.examples.strategies.freqtrade_ported.diamond import Diamond
from nautilus_trader.examples.strategies.freqtrade_ported.diamond import DiamondConfig
from nautilus_trader.examples.strategies.freqtrade_ported.does_nothing import DoesNothing
from nautilus_trader.examples.strategies.freqtrade_ported.does_nothing import DoesNothingConfig
from nautilus_trader.examples.strategies.freqtrade_ported.ema_skip_pump import EmaSkipPump
from nautilus_trader.examples.strategies.freqtrade_ported.ema_skip_pump import EmaSkipPumpConfig
from nautilus_trader.examples.strategies.freqtrade_ported.f_adx_sma import FAdxSma
from nautilus_trader.examples.strategies.freqtrade_ported.f_adx_sma import FAdxSmaConfig
from nautilus_trader.examples.strategies.freqtrade_ported.f_supertrend import FSupertrend
from nautilus_trader.examples.strategies.freqtrade_ported.f_supertrend import FSupertrendConfig
from nautilus_trader.examples.strategies.freqtrade_ported.f_ott import FOtt
from nautilus_trader.examples.strategies.freqtrade_ported.f_ott import FOttConfig
from nautilus_trader.examples.strategies.freqtrade_ported.f_reinforced import FReinforced
from nautilus_trader.examples.strategies.freqtrade_ported.f_reinforced import FReinforcedConfig
from nautilus_trader.examples.strategies.freqtrade_ported.f_sample import FSample
from nautilus_trader.examples.strategies.freqtrade_ported.f_sample import FSampleConfig
from nautilus_trader.examples.strategies.freqtrade_ported.fixed_risk_reward_loss import FixedRiskRewardLoss
from nautilus_trader.examples.strategies.freqtrade_ported.fixed_risk_reward_loss import FixedRiskRewardLossConfig
from nautilus_trader.examples.strategies.freqtrade_ported.god_stra import GodStra
from nautilus_trader.examples.strategies.freqtrade_ported.god_stra import GodStraConfig
from nautilus_trader.examples.strategies.freqtrade_ported.heracles import Heracles
from nautilus_trader.examples.strategies.freqtrade_ported.heracles import HeraclesConfig
from nautilus_trader.examples.strategies.freqtrade_ported.hlhb import Hlhb
from nautilus_trader.examples.strategies.freqtrade_ported.hlhb import HlhbConfig
from nautilus_trader.examples.strategies.freqtrade_ported.hour_based import HourBased
from nautilus_trader.examples.strategies.freqtrade_ported.hour_based import HourBasedConfig
from nautilus_trader.examples.strategies.freqtrade_ported.informative_sample import InformativeSample
from nautilus_trader.examples.strategies.freqtrade_ported.informative_sample import InformativeSampleConfig
from nautilus_trader.examples.strategies.freqtrade_ported.low_bb import LowBb
from nautilus_trader.examples.strategies.freqtrade_ported.low_bb import LowBbConfig
from nautilus_trader.examples.strategies.freqtrade_ported.macd_strategy import MacdStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.macd_strategy import MacdStrategyConfig
from nautilus_trader.examples.strategies.freqtrade_ported.macd_strategy_crossed import MacdStrategyCrossed
from nautilus_trader.examples.strategies.freqtrade_ported.macd_strategy_crossed import MacdStrategyCrossedConfig
from nautilus_trader.examples.strategies.freqtrade_ported.mab_stra import MabStra
from nautilus_trader.examples.strategies.freqtrade_ported.mab_stra import MabStraConfig
from nautilus_trader.examples.strategies.freqtrade_ported.multi_ma import MultiMa
from nautilus_trader.examples.strategies.freqtrade_ported.multi_ma import MultiMaConfig
from nautilus_trader.examples.strategies.freqtrade_ported.multi_rsi import MultiRsi
from nautilus_trader.examples.strategies.freqtrade_ported.multi_rsi import MultiRsiConfig
from nautilus_trader.examples.strategies.freqtrade_ported.multi_tf import MultiTf
from nautilus_trader.examples.strategies.freqtrade_ported.multi_tf import MultiTfConfig
from nautilus_trader.examples.strategies.freqtrade_ported.pattern_recognition import PatternRecognition
from nautilus_trader.examples.strategies.freqtrade_ported.pattern_recognition import PatternRecognitionConfig
from nautilus_trader.examples.strategies.freqtrade_ported.power_tower import PowerTower
from nautilus_trader.examples.strategies.freqtrade_ported.power_tower import PowerTowerConfig
from nautilus_trader.examples.strategies.freqtrade_ported.quickie import Quickie
from nautilus_trader.examples.strategies.freqtrade_ported.quickie import QuickieConfig
from nautilus_trader.examples.strategies.freqtrade_ported.reinforced_quickie import ReinforcedQuickie
from nautilus_trader.examples.strategies.freqtrade_ported.reinforced_quickie import ReinforcedQuickieConfig
from nautilus_trader.examples.strategies.freqtrade_ported.reinforced_average import ReinforcedAverage
from nautilus_trader.examples.strategies.freqtrade_ported.reinforced_average import ReinforcedAverageConfig
from nautilus_trader.examples.strategies.freqtrade_ported.reinforced_smooth_scalp import ReinforcedSmoothScalp
from nautilus_trader.examples.strategies.freqtrade_ported.reinforced_smooth_scalp import ReinforcedSmoothScalpConfig
from nautilus_trader.examples.strategies.freqtrade_ported.scalp import Scalp
from nautilus_trader.examples.strategies.freqtrade_ported.scalp import ScalpConfig
from nautilus_trader.examples.strategies.freqtrade_ported.simple_strategy import Simple
from nautilus_trader.examples.strategies.freqtrade_ported.simple_strategy import SimpleConfig
from nautilus_trader.examples.strategies.freqtrade_ported.smooth_scalp import SmoothScalp
from nautilus_trader.examples.strategies.freqtrade_ported.smooth_scalp import SmoothScalpConfig
from nautilus_trader.examples.strategies.freqtrade_ported.smooth_operator import SmoothOperator
from nautilus_trader.examples.strategies.freqtrade_ported.smooth_operator import SmoothOperatorConfig
from nautilus_trader.examples.strategies.freqtrade_ported.strategy001 import Strategy001
from nautilus_trader.examples.strategies.freqtrade_ported.strategy001 import Strategy001Config
from nautilus_trader.examples.strategies.freqtrade_ported.strategy001_custom_exit import Strategy001CustomExit
from nautilus_trader.examples.strategies.freqtrade_ported.strategy001_custom_exit import Strategy001CustomExitConfig
from nautilus_trader.examples.strategies.freqtrade_ported.strategy002 import Strategy002
from nautilus_trader.examples.strategies.freqtrade_ported.strategy002 import Strategy002Config
from nautilus_trader.examples.strategies.freqtrade_ported.strategy003 import Strategy003
from nautilus_trader.examples.strategies.freqtrade_ported.strategy003 import Strategy003Config
from nautilus_trader.examples.strategies.freqtrade_ported.strategy004 import Strategy004
from nautilus_trader.examples.strategies.freqtrade_ported.strategy004 import Strategy004Config
from nautilus_trader.examples.strategies.freqtrade_ported.strategy005 import Strategy005
from nautilus_trader.examples.strategies.freqtrade_ported.strategy005 import Strategy005Config
from nautilus_trader.examples.strategies.freqtrade_ported.supertrend import Supertrend
from nautilus_trader.examples.strategies.freqtrade_ported.supertrend import SupertrendConfig
from nautilus_trader.examples.strategies.freqtrade_ported.td_sequential import TdSequentialStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.td_sequential import TdSequentialStrategyConfig
from nautilus_trader.examples.strategies.freqtrade_ported.trend_following import TrendFollowing
from nautilus_trader.examples.strategies.freqtrade_ported.trend_following import TrendFollowingConfig
from nautilus_trader.examples.strategies.freqtrade_ported.trend_rider import TrendRider
from nautilus_trader.examples.strategies.freqtrade_ported.trend_rider import TrendRiderConfig
from nautilus_trader.examples.strategies.freqtrade_ported.swing_high_to_sky import SwingHighToSky
from nautilus_trader.examples.strategies.freqtrade_ported.swing_high_to_sky import SwingHighToSkyConfig
from nautilus_trader.examples.strategies.freqtrade_ported.technical_example import TechnicalExample
from nautilus_trader.examples.strategies.freqtrade_ported.technical_example import TechnicalExampleConfig
from nautilus_trader.examples.strategies.freqtrade_ported.universal_macd import UniversalMacd
from nautilus_trader.examples.strategies.freqtrade_ported.universal_macd import UniversalMacdConfig
from nautilus_trader.examples.strategies.freqtrade_ported.volatility_system import VolatilitySystem
from nautilus_trader.examples.strategies.freqtrade_ported.volatility_system import VolatilitySystemConfig


__all__ = [
    "AdxMomentum",
    "AdxMomentumConfig",
    "AdxSmas",
    "AdxSmasConfig",
    "AsdtsRockwell",
    "AsdtsRockwellConfig",
    "AverageStrategy",
    "AverageStrategyConfig",
    "AwesomeMacd",
    "AwesomeMacdConfig",
    "Bandtastic",
    "BandtasticConfig",
    "BbandRsi",
    "BbandRsiConfig",
    "BinHv27",
    "BinHv27Config",
    "BinHv45",
    "BinHv45Config",
    "BreakEven",
    "BreakEvenConfig",
    "ClucMay72018",
    "ClucMay72018Config",
    "CciStrategy",
    "CciStrategyConfig",
    "CofiBit",
    "CofiBitConfig",
    "CombinedBinHAndCluc",
    "CombinedBinHAndClucConfig",
    "CmcWinner",
    "CmcWinnerConfig",
    "CustomStoplossWithPsar",
    "CustomStoplossWithPsarConfig",
    "Diamond",
    "DiamondConfig",
    "DoesNothing",
    "DoesNothingConfig",
    "EmaSkipPump",
    "EmaSkipPumpConfig",
    "FAdxSma",
    "FAdxSmaConfig",
    "FREQTRADE_STRATEGY_CATALOG",
    "FSupertrend",
    "FSupertrendConfig",
    "FOtt",
    "FOttConfig",
    "FReinforced",
    "FReinforcedConfig",
    "FSample",
    "FSampleConfig",
    "FixedRiskRewardLoss",
    "FixedRiskRewardLossConfig",
    "GodStra",
    "GodStraConfig",
    "Heracles",
    "HeraclesConfig",
    "FreqtradeLongOnlyStrategy",
    "FreqtradeLongShortStrategy",
    "FreqtradePortConfig",
    "Hlhb",
    "HlhbConfig",
    "HourBased",
    "HourBasedConfig",
    "InformativeSample",
    "InformativeSampleConfig",
    "LowBb",
    "LowBbConfig",
    "MacdStrategy",
    "MacdStrategyConfig",
    "MacdStrategyCrossed",
    "MacdStrategyCrossedConfig",
    "MabStra",
    "MabStraConfig",
    "MultiMa",
    "MultiMaConfig",
    "MultiRsi",
    "MultiRsiConfig",
    "MultiTf",
    "MultiTfConfig",
    "PatternRecognition",
    "PatternRecognitionConfig",
    "PortStatus",
    "PowerTower",
    "PowerTowerConfig",
    "Quickie",
    "QuickieConfig",
    "ReinforcedQuickie",
    "ReinforcedQuickieConfig",
    "ReinforcedAverage",
    "ReinforcedAverageConfig",
    "ReinforcedSmoothScalp",
    "ReinforcedSmoothScalpConfig",
    "Scalp",
    "ScalpConfig",
    "Simple",
    "SimpleConfig",
    "SmoothScalp",
    "SmoothScalpConfig",
    "SmoothOperator",
    "SmoothOperatorConfig",
    "Strategy001",
    "Strategy001Config",
    "Strategy001CustomExit",
    "Strategy001CustomExitConfig",
    "Strategy002",
    "Strategy002Config",
    "Strategy003",
    "Strategy003Config",
    "Strategy004",
    "Strategy004Config",
    "Strategy005",
    "Strategy005Config",
    "Supertrend",
    "SupertrendConfig",
    "TdSequentialStrategy",
    "TdSequentialStrategyConfig",
    "TrendFollowing",
    "TrendFollowingConfig",
    "TrendRider",
    "TrendRiderConfig",
    "SwingHighToSky",
    "SwingHighToSkyConfig",
    "TechnicalExample",
    "TechnicalExampleConfig",
    "UniversalMacd",
    "UniversalMacdConfig",
    "VolatilitySystem",
    "VolatilitySystemConfig",
]
