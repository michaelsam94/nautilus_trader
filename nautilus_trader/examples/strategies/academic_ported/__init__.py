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

"""paperswithbacktest awesome-systematic-trading academic strategy ports."""

from nautilus_trader.examples.strategies.academic_ported.asset_class_momentum import AssetClassMomentum
from nautilus_trader.examples.strategies.academic_ported.asset_class_momentum import AssetClassMomentumConfig
from nautilus_trader.examples.strategies.academic_ported.asset_class_trend import AssetClassTrend
from nautilus_trader.examples.strategies.academic_ported.asset_class_trend import AssetClassTrendConfig
from nautilus_trader.examples.strategies.academic_ported.bitcoin_seasonality import BitcoinSeasonality
from nautilus_trader.examples.strategies.academic_ported.bitcoin_seasonality import BitcoinSeasonalityConfig
from nautilus_trader.examples.strategies.academic_ported.carry_momentum import CarryMomentum
from nautilus_trader.examples.strategies.academic_ported.carry_momentum import CarryMomentumConfig
from nautilus_trader.examples.strategies.academic_ported.catalog import ACADEMIC_STRATEGY_CATALOG
from nautilus_trader.examples.strategies.academic_ported.combining_factors import CombiningFactors
from nautilus_trader.examples.strategies.academic_ported.combining_factors import CombiningFactorsConfig
from nautilus_trader.examples.strategies.academic_ported.commodity_momentum import CommodityMomentum
from nautilus_trader.examples.strategies.academic_ported.commodity_momentum import CommodityMomentumConfig
from nautilus_trader.examples.strategies.academic_ported.consistent_momentum import ConsistentMomentum
from nautilus_trader.examples.strategies.academic_ported.consistent_momentum import ConsistentMomentumConfig
from nautilus_trader.examples.strategies.academic_ported.country_etf_pairs import CountryEtfPairs
from nautilus_trader.examples.strategies.academic_ported.country_etf_pairs import CountryEtfPairsConfig
from nautilus_trader.examples.strategies.academic_ported.crude_oil_equity import CrudeOilEquity
from nautilus_trader.examples.strategies.academic_ported.crude_oil_equity import CrudeOilEquityConfig
from nautilus_trader.examples.strategies.academic_ported.cross_sectional_momentum import CrossSectionalMomentum
from nautilus_trader.examples.strategies.academic_ported.cross_sectional_momentum import CrossSectionalMomentumConfig
from nautilus_trader.examples.strategies.academic_ported.currency_momentum import CurrencyMomentum
from nautilus_trader.examples.strategies.academic_ported.currency_momentum import CurrencyMomentumConfig
from nautilus_trader.examples.strategies.academic_ported.january_barometer import JanuaryBarometer
from nautilus_trader.examples.strategies.academic_ported.january_barometer import JanuaryBarometerConfig
from nautilus_trader.examples.strategies.academic_ported.low_beta import LowBeta
from nautilus_trader.examples.strategies.academic_ported.low_beta import LowBetaConfig
from nautilus_trader.examples.strategies.academic_ported.low_volatility import LowVolatility
from nautilus_trader.examples.strategies.academic_ported.low_volatility import LowVolatilityConfig
from nautilus_trader.examples.strategies.academic_ported.momentum_volatility import MomentumVolatility
from nautilus_trader.examples.strategies.academic_ported.momentum_volatility import MomentumVolatilityConfig
from nautilus_trader.examples.strategies.academic_ported.overnight_sentiment import OvernightSentiment
from nautilus_trader.examples.strategies.academic_ported.overnight_sentiment import OvernightSentimentConfig
from nautilus_trader.examples.strategies.academic_ported.option_expiration_week import OptionExpirationWeek
from nautilus_trader.examples.strategies.academic_ported.option_expiration_week import OptionExpirationWeekConfig
from nautilus_trader.examples.strategies.academic_ported.paired_switching import PairedSwitching
from nautilus_trader.examples.strategies.academic_ported.paired_switching import PairedSwitchingConfig
from nautilus_trader.examples.strategies.academic_ported.payday_anomaly import PaydayAnomaly
from nautilus_trader.examples.strategies.academic_ported.payday_anomaly import PaydayAnomalyConfig
from nautilus_trader.examples.strategies.academic_ported.residual_momentum import ResidualMomentum
from nautilus_trader.examples.strategies.academic_ported.residual_momentum import ResidualMomentumConfig
from nautilus_trader.examples.strategies.academic_ported.return_asymmetry import ReturnAsymmetry
from nautilus_trader.examples.strategies.academic_ported.return_asymmetry import ReturnAsymmetryConfig
from nautilus_trader.examples.strategies.academic_ported.sector_momentum import SectorMomentum
from nautilus_trader.examples.strategies.academic_ported.sector_momentum import SectorMomentumConfig
from nautilus_trader.examples.strategies.academic_ported.short_term_reversal import ShortTermReversal
from nautilus_trader.examples.strategies.academic_ported.short_term_reversal import ShortTermReversalConfig
from nautilus_trader.examples.strategies.academic_ported.skewness_effect import SkewnessEffect
from nautilus_trader.examples.strategies.academic_ported.skewness_effect import SkewnessEffectConfig
from nautilus_trader.examples.strategies.academic_ported.style_rotation import StyleRotation
from nautilus_trader.examples.strategies.academic_ported.style_rotation import StyleRotationConfig
from nautilus_trader.examples.strategies.academic_ported.term_structure_proxy import TermStructureProxy
from nautilus_trader.examples.strategies.academic_ported.term_structure_proxy import TermStructureProxyConfig
from nautilus_trader.examples.strategies.academic_ported.time_series_momentum import TimeSeriesMomentum
from nautilus_trader.examples.strategies.academic_ported.time_series_momentum import TimeSeriesMomentumConfig
from nautilus_trader.examples.strategies.academic_ported.turn_of_the_month import TurnOfTheMonth
from nautilus_trader.examples.strategies.academic_ported.turn_of_the_month import TurnOfTheMonthConfig
from nautilus_trader.examples.strategies.academic_ported.twelve_month_cycle import TwelveMonthCycle
from nautilus_trader.examples.strategies.academic_ported.twelve_month_cycle import TwelveMonthCycleConfig
from nautilus_trader.examples.strategies.academic_ported.value_proxy import ValueProxy
from nautilus_trader.examples.strategies.academic_ported.value_proxy import ValueProxyConfig
from nautilus_trader.examples.strategies.academic_ported.vol_risk_premium import VolRiskPremium
from nautilus_trader.examples.strategies.academic_ported.vol_risk_premium import VolRiskPremiumConfig
from nautilus_trader.examples.strategies.academic_ported.weeks_52_high import Weeks52High
from nautilus_trader.examples.strategies.academic_ported.weeks_52_high import Weeks52HighConfig
from nautilus_trader.examples.strategies.academic_ported.weekly_reversal import WeeklyReversal
from nautilus_trader.examples.strategies.academic_ported.weekly_reversal import WeeklyReversalConfig
from nautilus_trader.examples.strategies.academic_ported.wti_brent_spread import WtiBrentSpread
from nautilus_trader.examples.strategies.academic_ported.wti_brent_spread import WtiBrentSpreadConfig


__all__ = [
    "ACADEMIC_STRATEGY_CATALOG",
    "AssetClassMomentum",
    "AssetClassMomentumConfig",
    "AssetClassTrend",
    "AssetClassTrendConfig",
    "BitcoinSeasonality",
    "BitcoinSeasonalityConfig",
    "CarryMomentum",
    "CarryMomentumConfig",
    "CombiningFactors",
    "CombiningFactorsConfig",
    "CommodityMomentum",
    "CommodityMomentumConfig",
    "ConsistentMomentum",
    "ConsistentMomentumConfig",
    "CountryEtfPairs",
    "CountryEtfPairsConfig",
    "CrudeOilEquity",
    "CrudeOilEquityConfig",
    "CrossSectionalMomentum",
    "CrossSectionalMomentumConfig",
    "CurrencyMomentum",
    "CurrencyMomentumConfig",
    "JanuaryBarometer",
    "JanuaryBarometerConfig",
    "LowBeta",
    "LowBetaConfig",
    "LowVolatility",
    "LowVolatilityConfig",
    "MomentumVolatility",
    "MomentumVolatilityConfig",
    "OptionExpirationWeek",
    "OptionExpirationWeekConfig",
    "OvernightSentiment",
    "OvernightSentimentConfig",
    "PairedSwitching",
    "PairedSwitchingConfig",
    "PaydayAnomaly",
    "PaydayAnomalyConfig",
    "ResidualMomentum",
    "ResidualMomentumConfig",
    "ReturnAsymmetry",
    "ReturnAsymmetryConfig",
    "SectorMomentum",
    "SectorMomentumConfig",
    "ShortTermReversal",
    "ShortTermReversalConfig",
    "SkewnessEffect",
    "SkewnessEffectConfig",
    "StyleRotation",
    "StyleRotationConfig",
    "TermStructureProxy",
    "TermStructureProxyConfig",
    "TimeSeriesMomentum",
    "TimeSeriesMomentumConfig",
    "TurnOfTheMonth",
    "TurnOfTheMonthConfig",
    "TwelveMonthCycle",
    "TwelveMonthCycleConfig",
    "ValueProxy",
    "ValueProxyConfig",
    "VolRiskPremium",
    "VolRiskPremiumConfig",
    "Weeks52High",
    "Weeks52HighConfig",
    "WeeklyReversal",
    "WeeklyReversalConfig",
    "WtiBrentSpread",
    "WtiBrentSpreadConfig",
]
