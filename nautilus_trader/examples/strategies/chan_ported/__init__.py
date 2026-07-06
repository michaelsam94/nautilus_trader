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

"""Ports of Ernest Chan (2013) *Algorithmic Trading* strategies."""

from nautilus_trader.examples.strategies.chan_ported.bollinger_spread_pairs import BollingerSpreadPairs
from nautilus_trader.examples.strategies.chan_ported.bollinger_spread_pairs import BollingerSpreadPairsConfig
from nautilus_trader.examples.strategies.chan_ported.buy_on_gap import BuyOnGap
from nautilus_trader.examples.strategies.chan_ported.buy_on_gap import BuyOnGapConfig
from nautilus_trader.examples.strategies.chan_ported.catalog import CHAN_STRATEGY_CATALOG
from nautilus_trader.examples.strategies.chan_ported.catalog import ChanStatus
from nautilus_trader.examples.strategies.chan_ported.catalog import catalog_summary
from nautilus_trader.examples.strategies.chan_ported.catalog import ported_modules
from nautilus_trader.examples.strategies.chan_ported.cross_sectional_mean_reversion import CrossSectionalMeanReversion
from nautilus_trader.examples.strategies.chan_ported.cross_sectional_mean_reversion import CrossSectionalMeanReversionConfig
from nautilus_trader.examples.strategies.chan_ported.currency_zscore_mr import CurrencyZscoreMr
from nautilus_trader.examples.strategies.chan_ported.currency_zscore_mr import CurrencyZscoreMrConfig
from nautilus_trader.examples.strategies.chan_ported.dedup import CHAN_DEDUP
from nautilus_trader.examples.strategies.chan_ported.futures_tsmom_staggered import FuturesTsmomStaggered
from nautilus_trader.examples.strategies.chan_ported.futures_tsmom_staggered import FuturesTsmomStaggeredConfig
from nautilus_trader.examples.strategies.chan_ported.johansen_portfolio_mr import JohansenPortfolioMr
from nautilus_trader.examples.strategies.chan_ported.johansen_portfolio_mr import JohansenPortfolioMrConfig
from nautilus_trader.examples.strategies.chan_ported.kalman_pairs import KalmanPairs
from nautilus_trader.examples.strategies.chan_ported.kalman_pairs import KalmanPairsConfig
from nautilus_trader.examples.strategies.chan_ported.leveraged_etf_rebalance import LeveragedEtfRebalance
from nautilus_trader.examples.strategies.chan_ported.leveraged_etf_rebalance import LeveragedEtfRebalanceConfig
from nautilus_trader.examples.strategies.chan_ported.linear_mean_reversion import LinearMeanReversion
from nautilus_trader.examples.strategies.chan_ported.linear_mean_reversion import LinearMeanReversionConfig
from nautilus_trader.examples.strategies.chan_ported.linear_spread_pairs import LinearSpreadPairs
from nautilus_trader.examples.strategies.chan_ported.linear_spread_pairs import LinearSpreadPairsConfig
from nautilus_trader.examples.strategies.chan_ported.log_spread_pairs import LogSpreadPairs
from nautilus_trader.examples.strategies.chan_ported.log_spread_pairs import LogSpreadPairsConfig
from nautilus_trader.examples.strategies.chan_ported.opening_gap_momentum import OpeningGapMomentum
from nautilus_trader.examples.strategies.chan_ported.opening_gap_momentum import OpeningGapMomentumConfig
from nautilus_trader.examples.strategies.chan_ported.ratio_spread_pairs import RatioSpreadPairs
from nautilus_trader.examples.strategies.chan_ported.ratio_spread_pairs import RatioSpreadPairsConfig
from nautilus_trader.examples.strategies.chan_ported.vol_equity_spread import VolEquitySpread
from nautilus_trader.examples.strategies.chan_ported.vol_equity_spread import VolEquitySpreadConfig


__all__ = [
    "BollingerSpreadPairs",
    "BollingerSpreadPairsConfig",
    "BuyOnGap",
    "BuyOnGapConfig",
    "CHAN_DEDUP",
    "CHAN_STRATEGY_CATALOG",
    "ChanStatus",
    "CrossSectionalMeanReversion",
    "CrossSectionalMeanReversionConfig",
    "CurrencyZscoreMr",
    "CurrencyZscoreMrConfig",
    "FuturesTsmomStaggered",
    "FuturesTsmomStaggeredConfig",
    "JohansenPortfolioMr",
    "JohansenPortfolioMrConfig",
    "KalmanPairs",
    "KalmanPairsConfig",
    "LeveragedEtfRebalance",
    "LeveragedEtfRebalanceConfig",
    "LinearMeanReversion",
    "LinearMeanReversionConfig",
    "LinearSpreadPairs",
    "LinearSpreadPairsConfig",
    "LogSpreadPairs",
    "LogSpreadPairsConfig",
    "OpeningGapMomentum",
    "OpeningGapMomentumConfig",
    "RatioSpreadPairs",
    "RatioSpreadPairsConfig",
    "VolEquitySpread",
    "VolEquitySpreadConfig",
    "catalog_summary",
    "ported_modules",
]
