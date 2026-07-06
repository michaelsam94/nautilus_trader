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

"""Dedup mapping: Chan (2013) strategies vs existing ported folders."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChanDedupEntry:
    chan_strategy: str
    duplicate_of: str | None
    nautilus_module: str | None
    reason: str


CHAN_DEDUP: dict[str, ChanDedupEntry] = {
    "etf_pairs_triplets": ChanDedupEntry(
        "ETF pairs (EWA-EWC)",
        "systematic_trading_ported.pair_trading.PairTrading",
        "chan_ported.johansen_portfolio_mr.JohansenPortfolioMr",
        "Pair z-score covered; triplet Johansen portfolio is separate port.",
    ),
    "quant_trading_pair_zscore": ChanDedupEntry(
        "Price spread z-score pairs",
        "systematic_trading_ported.pair_trading.PairTrading",
        "chan_ported.linear_spread_pairs.LinearSpreadPairs",
        "quant-trading uses threshold z-entry; Chan 3.1 uses adaptive OLS linear spread.",
    ),
    "academic_country_etf_pairs": ChanDedupEntry(
        "Country ETF pairs",
        "academic_ported.country_etf_pairs.CountryEtfPairs",
        None,
        "Academic script already ports ETF pair mean reversion.",
    ),
    "academic_time_series_momentum": ChanDedupEntry(
        "Time-series momentum (ROC)",
        "academic_ported.time_series_momentum.TimeSeriesMomentum",
        "chan_ported.futures_tsmom_staggered.FuturesTsmomStaggered",
        "Academic ROC sign; Chan 6.1 staggered hold is ported separately.",
    ),
    "cross_sectional_momentum_stocks": ChanDedupEntry(
        "Cross-sectional momentum stocks",
        "academic_ported.cross_sectional_momentum.CrossSectionalMomentum",
        None,
        "12-1 month momentum single-asset port equivalent.",
    ),
    "backtrader_ou_mean_reversion": ChanDedupEntry(
        "OU mean reversion",
        "backtrader_ported.ou_mean_reversion.OuMeanReversion",
        "chan_ported.linear_mean_reversion.LinearMeanReversion",
        "Different model: OU process vs Chan rolling z-score linear MR.",
    ),
    "freqtrade_bollinger_single": ChanDedupEntry(
        "Single-asset Bollinger MR",
        "freqtrade_ported.f_sample.FSample",
        "chan_ported.bollinger_spread_pairs.BollingerSpreadPairs",
        "Freqtrade BB on single asset; Chan 3.2 is spread BB on pairs.",
    ),
    "vectorbt_dual_momentum": ChanDedupEntry(
        "Dual momentum rotation",
        "vectorbt_ported.dual_momentum_rotation.DualMomentumRotation",
        None,
        "Antonacci dual momentum; not Chan cross-sectional rank.",
    ),
    "intraday_cross_sectional_mr": ChanDedupEntry(
        "Intraday cross-sectional MR",
        "chan_ported.cross_sectional_mean_reversion.CrossSectionalMeanReversion",
        None,
        "Same reversal signal; frequency differs only.",
    ),
    "futures_intermarket_spread": ChanDedupEntry(
        "Futures intermarket spread",
        "chan_ported.vol_equity_spread.VolEquitySpread",
        None,
        "VX-vs-ES intermarket covered by vol_equity_spread.",
    ),
}
