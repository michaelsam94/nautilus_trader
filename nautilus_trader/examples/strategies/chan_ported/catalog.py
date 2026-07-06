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

"""
Catalog for Ernest Chan — *Algorithmic Trading: Winning Strategies and Their Rationale* (2013).

Source: /Users/michael/Downloads/Algorithmic Trading - Winning Strategies and Their Rationale 2013.pdf
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ChanStatus(StrEnum):
    PORTED = "ported"
    PARTIAL = "partial"
    DEDUP_SKIP = "dedup_skip"
    BLOCKED = "blocked"
    METHODOLOGY = "methodology"


@dataclass(frozen=True)
class ChanCatalogEntry:
    book_ref: str
    chapter: int
    page: int
    example: str | None
    status: ChanStatus
    nautilus_module: str | None = None
    dedup_target: str | None = None
    reason: str = ""


CHAN_STRATEGY_CATALOG: dict[str, ChanCatalogEntry] = {
    # Ch.1 — methodology
    "hypothesis_testing": ChanCatalogEntry(
        "Ch.1 Statistical Significance", 1, 34, "1.1", ChanStatus.METHODOLOGY,
        reason="Backtesting methodology; not a trading signal.",
    ),
    # Ch.2 — mean reversion foundations
    "adf_stationarity_test": ChanCatalogEntry(
        "Ch.2 ADF Test", 2, 60, "2.1", ChanStatus.METHODOLOGY,
        reason="Diagnostic test; used inside pair gates.",
    ),
    "hurst_variance_ratio": ChanCatalogEntry(
        "Ch.2 Hurst / Variance Ratio", 2, 62, "2.2-2.3", ChanStatus.METHODOLOGY,
        reason="Stationarity diagnostics.",
    ),
    "half_life_estimation": ChanCatalogEntry(
        "Ch.2 Half-Life", 2, 64, "2.4", ChanStatus.METHODOLOGY,
        reason="half_life_from_series() in indicators.py.",
    ),
    "linear_mean_reversion": ChanCatalogEntry(
        "Ch.2 Linear MR single asset", 2, 66, "2.5", ChanStatus.PORTED,
        "chan_ported.linear_mean_reversion.LinearMeanReversion",
    ),
    "cadf_cointegration_test": ChanCatalogEntry(
        "Ch.2 CADF cointegration", 2, 69, "2.6", ChanStatus.METHODOLOGY,
        reason="Engle-Granger gate in systematic_trading_ported.pair_trading.",
    ),
    "johansen_cointegration": ChanCatalogEntry(
        "Ch.2 Johansen test", 2, 72, "2.7", ChanStatus.METHODOLOGY,
        reason="Offline eigenvector estimation; weights in johansen_portfolio_mr.",
    ),
    "johansen_portfolio_mr": ChanCatalogEntry(
        "Ch.2 Linear MR portfolio", 2, 76, "2.8", ChanStatus.PORTED,
        "chan_ported.johansen_portfolio_mr.JohansenPortfolioMr",
    ),
    # Ch.3 — implementing mean reversion
    "price_spread_pairs": ChanCatalogEntry(
        "Ch.3 Price spread pairs", 3, 82, "3.1", ChanStatus.PORTED,
        "chan_ported.linear_spread_pairs.LinearSpreadPairs",
    ),
    "log_spread_pairs": ChanCatalogEntry(
        "Ch.3 Log spread pairs", 3, 82, "3.1", ChanStatus.PORTED,
        "chan_ported.log_spread_pairs.LogSpreadPairs",
    ),
    "ratio_spread_pairs": ChanCatalogEntry(
        "Ch.3 Ratio pairs", 3, 82, "3.1", ChanStatus.PORTED,
        "chan_ported.ratio_spread_pairs.RatioSpreadPairs",
    ),
    "bollinger_spread_pairs": ChanCatalogEntry(
        "Ch.3 Bollinger spread MR", 3, 88, "3.2", ChanStatus.PORTED,
        "chan_ported.bollinger_spread_pairs.BollingerSpreadPairs",
    ),
    "scaling_in": ChanCatalogEntry(
        "Ch.3 Scaling-in", 3, 90, None, ChanStatus.METHODOLOGY,
        reason="Position-sizing technique; not a standalone signal.",
    ),
    "kalman_pairs": ChanCatalogEntry(
        "Ch.3 Kalman filter pairs", 3, 92, "3.3", ChanStatus.PORTED,
        "chan_ported.kalman_pairs.KalmanPairs",
    ),
    "kalman_market_making": ChanCatalogEntry(
        "Ch.3 Kalman market making", 3, 100, None, ChanStatus.BLOCKED,
        reason="Requires tick data and limit-order book simulation.",
    ),
    # Ch.4 — stocks and ETFs
    "etf_pairs_triplets": ChanCatalogEntry(
        "Ch.4 ETF pairs/triplets", 4, 109, None, ChanStatus.DEDUP_SKIP,
        dedup_target="systematic_trading_ported.pair_trading.PairTrading",
        reason="Generic ETF pair z-score; Chan adds triplet Johansen weights via johansen_portfolio_mr.",
    ),
    "buy_on_gap": ChanCatalogEntry(
        "Ch.4 Buy-on-gap intraday MR", 4, 110, "4.1", ChanStatus.PORTED,
        "chan_ported.buy_on_gap.BuyOnGap",
    ),
    "etf_component_arbitrage": ChanCatalogEntry(
        "Ch.4 ETF vs components arb", 4, 114, "4.2", ChanStatus.BLOCKED,
        reason="Requires full ETF constituent basket and intraday component prices.",
    ),
    "cross_sectional_mean_reversion": ChanCatalogEntry(
        "Ch.4 Cross-sectional MR", 4, 120, "4.3", ChanStatus.PARTIAL,
        "chan_ported.cross_sectional_mean_reversion.CrossSectionalMeanReversion",
        reason="Single-asset proxy; full S&P 500 rank needs universe.",
    ),
    "intraday_cross_sectional_mr": ChanCatalogEntry(
        "Ch.4 Intraday linear long-short", 4, 122, "4.4", ChanStatus.DEDUP_SKIP,
        dedup_target="chan_ported.cross_sectional_mean_reversion.CrossSectionalMeanReversion",
        reason="Same short-horizon reversal signal at intraday frequency.",
    ),
    # Ch.5 — currencies and futures
    "currency_cross_mr": ChanCatalogEntry(
        "Ch.5 Currency cross-rate MR", 5, 126, "5.1-5.2", ChanStatus.PORTED,
        "chan_ported.currency_zscore_mr.CurrencyZscoreMr",
    ),
    "currency_rollover_carry": ChanCatalogEntry(
        "Ch.5 Rollover interest", 5, 131, None, ChanStatus.METHODOLOGY,
        reason="FX carry adjustment; wire via Nautilus funding model.",
    ),
    "calendar_spread_mr": ChanCatalogEntry(
        "Ch.5 Calendar spread MR", 5, 141, "5.4", ChanStatus.BLOCKED,
        reason="Requires multi-contract futures chain (CL calendar γ roll series).",
    ),
    "roll_return_estimation": ChanCatalogEntry(
        "Ch.5 Spot/roll returns CRM", 5, 133, "5.3", ChanStatus.METHODOLOGY,
        reason="Constant returns model estimation; input to calendar spread.",
    ),
    "vol_equity_intermarket": ChanCatalogEntry(
        "Ch.5 Vol futures vs equity", 5, 147, None, ChanStatus.PORTED,
        "chan_ported.vol_equity_spread.VolEquitySpread",
    ),
    "futures_intermarket_spread": ChanCatalogEntry(
        "Ch.5 Futures intermarket", 5, 145, None, ChanStatus.DEDUP_SKIP,
        dedup_target="chan_ported.vol_equity_spread.VolEquitySpread",
        reason="VX-vs-ES covered by vol_equity_spread.",
    ),
    # Ch.6 — interday momentum
    "time_series_momentum_futures": ChanCatalogEntry(
        "Ch.6 Time-series momentum", 6, 155, "6.1", ChanStatus.PORTED,
        "chan_ported.futures_tsmom_staggered.FuturesTsmomStaggered",
        reason="Staggered hold-days overlay distinct from academic_ported TSMOM.",
    ),
    "futures_etf_roll_arbitrage": ChanCatalogEntry(
        "Ch.6 Futures vs ETF roll arb", 6, 159, None, ChanStatus.BLOCKED,
        reason="Requires simultaneous futures curve and ETF roll-return series.",
    ),
    "cross_sectional_momentum_stocks": ChanCatalogEntry(
        "Ch.6 Cross-sectional momentum", 6, 162, "6.2", ChanStatus.DEDUP_SKIP,
        dedup_target="academic_ported.cross_sectional_momentum.CrossSectionalMomentum",
        reason="12-1 month UMD single-asset port covers core signal.",
    ),
    "cross_sectional_momentum_futures": ChanCatalogEntry(
        "Ch.6 Cross-sectional futures mom", 6, 155, None, ChanStatus.DEDUP_SKIP,
        dedup_target="chan_ported.futures_tsmom_staggered.FuturesTsmomStaggered",
        reason="Rank momentum across futures; single-future port uses TSMOM.",
    ),
    "news_sentiment_factor": ChanCatalogEntry(
        "Ch.6 News sentiment", 6, 166, None, ChanStatus.BLOCKED,
        reason="Requires NLP news sentiment feed.",
    ),
    "mutual_fund_fire_sale": ChanCatalogEntry(
        "Ch.6 Fund flow momentum", 6, 167, None, ChanStatus.BLOCKED,
        reason="Requires mutual-fund flow / 13-F data.",
    ),
    # Ch.7 — intraday momentum
    "opening_gap_momentum": ChanCatalogEntry(
        "Ch.7 Opening gap momentum", 7, 174, "7.1", ChanStatus.PORTED,
        "chan_ported.opening_gap_momentum.OpeningGapMomentum",
    ),
    "pead": ChanCatalogEntry(
        "Ch.7 Post-earnings drift", 7, 176, "7.2", ChanStatus.BLOCKED,
        reason="Requires earnings announcement calendar (earnann matrix).",
    ),
    "event_drift_other": ChanCatalogEntry(
        "Ch.7 Other event drift", 7, 180, None, ChanStatus.BLOCKED,
        reason="Requires corporate event calendar.",
    ),
    "leveraged_etf_rebalance": ChanCatalogEntry(
        "Ch.7 Leveraged ETF", 7, 181, None, ChanStatus.PORTED,
        "chan_ported.leveraged_etf_rebalance.LeveragedEtfRebalance",
    ),
    "high_frequency_strategies": ChanCatalogEntry(
        "Ch.7 High-frequency", 7, 182, None, ChanStatus.BLOCKED,
        reason="Requires tick/order-book data and sub-second execution.",
    ),
    # Ch.8 — risk management (not alpha)
    "kelly_leverage": ChanCatalogEntry(
        "Ch.8 Kelly formula", 8, 190, None, ChanStatus.METHODOLOGY,
        reason="Position sizing; use Nautilus risk components.",
    ),
    "cppi": ChanCatalogEntry(
        "Ch.8 CPPI", 8, 198, None, ChanStatus.METHODOLOGY,
        reason="Portfolio insurance overlay.",
    ),
    "stop_loss": ChanCatalogEntry(
        "Ch.8 Stop loss", 8, 200, None, ChanStatus.METHODOLOGY,
        reason="Risk overlay; implement via check_custom_stoploss.",
    ),
    # Overlap with other ports
    "quant_trading_pair_zscore": ChanCatalogEntry(
        "Overlap: quant-trading pairs", 3, 82, None, ChanStatus.DEDUP_SKIP,
        dedup_target="systematic_trading_ported.pair_trading.PairTrading",
        reason="je-suis-tm pair z-score with Engle-Granger gate; Chan linear spread ported separately.",
    ),
    "academic_country_etf_pairs": ChanCatalogEntry(
        "Overlap: country ETF pairs", 4, 109, None, ChanStatus.DEDUP_SKIP,
        dedup_target="academic_ported.country_etf_pairs.CountryEtfPairs",
        reason="Academic country-ETF pairs script covers ETF pair concept.",
    ),
    "academic_time_series_momentum": ChanCatalogEntry(
        "Overlap: TSMOM paper", 6, 152, None, ChanStatus.DEDUP_SKIP,
        dedup_target="academic_ported.time_series_momentum.TimeSeriesMomentum",
        reason="Moskowitz TSMOM; Chan 6.1 adds hold-days stagger in futures_tsmom_staggered.",
    ),
    "backtrader_ou_mean_reversion": ChanCatalogEntry(
        "Overlap: OU MR", 2, 66, None, ChanStatus.DEDUP_SKIP,
        dedup_target="backtrader_ported.ou_mean_reversion.OuMeanReversion",
        reason="OU z-score variant; Chan linear MR uses rolling MA z-score.",
    ),
}


def catalog_summary() -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in CHAN_STRATEGY_CATALOG.values():
        counts[entry.status] = counts.get(entry.status, 0) + 1
    return counts


def ported_modules() -> list[str]:
    return [
        e.nautilus_module
        for e in CHAN_STRATEGY_CATALOG.values()
        if e.status in (ChanStatus.PORTED, ChanStatus.PARTIAL) and e.nautilus_module
    ]
