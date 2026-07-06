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

"""Catalog for paperswithbacktest ``static/strategies/`` scripts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AcademicStatus(StrEnum):
    PORTED = "ported"
    PARTIAL = "partial"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class AcademicCatalogEntry:
    source_file: str
    nautilus_module: str | None
    status: AcademicStatus
    reason: str = ""


_BLOCK_REASON = (
    "QuantConnect universe/factor/portfolio script; requires multi-asset fundamentals."
)

_UPSTREAM_FILES: tuple[str, ...] = (
    "12-month-cycle-in-cross-section-of-stocks-returns",
    "52-weeks-high-effect-in-stocks",
    "accrual-anomaly",
    "asset-class-momentum-rotational-system",
    "asset-class-trend-following",
    "asset-growth-effect",
    "betting-against-beta-factor-in-country-equity-indexes",
    "betting-against-beta-factor-in-stocks",
    "combining-fundamental-fscore-and-equity-short-term-reversals",
    "combining-smart-factors-momentum-and-market-portfolio",
    "consistent-momentum-strategy",
    "crude-oil-predicts-equity-returns",
    "currency-momentum-factor",
    "currency-value-factor-ppp-strategy",
    "dispersion-trading",
    "dollar-carry-trade",
    "earnings-announcement-premium",
    "earnings-announcements-combined-with-stock-repurchases",
    "earnings-quality-factor",
    "esg-factor-momentum-strategy",
    "fed-model",
    "fx-carry-trade",
    "how-to-use-lexical-density-of-company-filings",
    "intraday-seasonality-in-bitcoin",
    "january-barometer",
    "low-volatility-factor-effect-in-stocks",
    "market-sentiment-and-an-overnight-anomaly",
    "momentum-and-reversal-combined-with-volatility-effect-in-stocks",
    "momentum-effect-in-commodities",
    "momentum-factor-and-style-rotation-effect",
    "momentum-factor-combined-with-asset-growth-effect",
    "momentum-factor-effect-in-stocks",
    "momentum-in-mutual-fund-returns",
    "option-expiration-week-effect",
    "paired-switching",
    "pairs-trading-with-country-etfs",
    "payday-anomaly",
    "rd-expenditures-and-stock-returns",
    "rebalancing-premium-in-cryptocurrencies",
    "residual-momentum-factor",
    "return-asymmetry-effect-in-commodity-futures",
    "reversal-during-earnings-announcements",
    "roa-effect-within-stocks",
    "sector-momentum-rotational-system",
    "short-interest-effect-long-short-version",
    "short-term-reversal-in-stocks",
    "short-term-reversal-with-futures",
    "skewness-effect-in-commodities",
    "small-capitalization-stocks-premium-anomaly",
    "soccer-clubs-stocks-arbitrage",
    "synthetic-lending-rates-predict-subsequent-market-return",
    "term-structure-effect-in-commodities",
    "time-series-momentum-effect",
    "trading-wti-brent-spread",
    "turn-of-the-month-in-equity-indexes",
    "value-and-momentum-factors-across-asset-classes",
    "value-book-to-market-factor",
    "value-factor-effect-within-countries",
    "volatility-risk-premium-effect",
)

_OVERRIDES: dict[str, AcademicCatalogEntry] = {
    "12-month-cycle-in-cross-section-of-stocks-returns": AcademicCatalogEntry(
        "12-month-cycle-in-cross-section-of-stocks-returns.py",
        "academic_ported.twelve_month_cycle.TwelveMonthCycle",
        AcademicStatus.PARTIAL,
        reason="Single-asset seasonal hold; cross-sectional decile sort omitted.",
    ),
    "52-weeks-high-effect-in-stocks": AcademicCatalogEntry(
        "52-weeks-high-effect-in-stocks.py",
        "academic_ported.weeks_52_high.Weeks52High",
        AcademicStatus.PARTIAL,
        reason="PRILAG proximity on one symbol; industry long/short omitted.",
    ),
    "asset-class-momentum-rotational-system": AcademicCatalogEntry(
        "asset-class-momentum-rotational-system.py",
        "academic_ported.asset_class_momentum.AssetClassMomentum",
        AcademicStatus.PARTIAL,
        reason="12m ROC on one ETF; top-3 rotation omitted.",
    ),
    "asset-class-trend-following": AcademicCatalogEntry(
        "asset-class-trend-following.py",
        "academic_ported.asset_class_trend.AssetClassTrend",
        AcademicStatus.PORTED,
        reason="10-month SMA filter on one instrument.",
    ),
    "betting-against-beta-factor-in-country-equity-indexes": AcademicCatalogEntry(
        "betting-against-beta-factor-in-country-equity-indexes.py",
        "academic_ported.low_beta.LowBeta",
        AcademicStatus.PARTIAL,
        reason="Low-beta filter on one index; long/short beta portfolios omitted.",
    ),
    "betting-against-beta-factor-in-stocks": AcademicCatalogEntry(
        "betting-against-beta-factor-in-stocks.py",
        "academic_ported.low_beta.LowBeta",
        AcademicStatus.PARTIAL,
        reason="Low-beta filter on one symbol; cross-sectional BAB omitted.",
    ),
    "combining-smart-factors-momentum-and-market-portfolio": AcademicCatalogEntry(
        "combining-smart-factors-momentum-and-market-portfolio.py",
        "academic_ported.combining_factors.CombiningFactors",
        AcademicStatus.PARTIAL,
        reason="Momentum plus low-vol composite; multi-factor portfolio omitted.",
    ),
    "consistent-momentum-strategy": AcademicCatalogEntry(
        "consistent-momentum-strategy.py",
        "academic_ported.consistent_momentum.ConsistentMomentum",
        AcademicStatus.PARTIAL,
        reason="Dual-window momentum on one symbol; decile portfolio omitted.",
    ),
    "crude-oil-predicts-equity-returns": AcademicCatalogEntry(
        "crude-oil-predicts-equity-returns.py",
        "academic_ported.crude_oil_equity.CrudeOilEquity",
        AcademicStatus.PARTIAL,
        reason="Monthly oil regression signal; cash leg and RF threshold omitted.",
    ),
    "currency-momentum-factor": AcademicCatalogEntry(
        "currency-momentum-factor.py",
        "academic_ported.currency_momentum.CurrencyMomentum",
        AcademicStatus.PARTIAL,
        reason="12m ROC on one FX future; top/bottom basket omitted.",
    ),
    "dollar-carry-trade": AcademicCatalogEntry(
        "dollar-carry-trade.py",
        "academic_ported.carry_momentum.CarryMomentum",
        AcademicStatus.PARTIAL,
        reason="3m momentum carry proxy; OECD rate data omitted.",
    ),
    "fx-carry-trade": AcademicCatalogEntry(
        "fx-carry-trade.py",
        "academic_ported.carry_momentum.CarryMomentum",
        AcademicStatus.PARTIAL,
        reason="3m momentum carry proxy; central-bank rate data omitted.",
    ),
    "intraday-seasonality-in-bitcoin": AcademicCatalogEntry(
        "intraday-seasonality-in-bitcoin.py",
        "academic_ported.bitcoin_seasonality.BitcoinSeasonality",
        AcademicStatus.PORTED,
        reason="22:00–00:00 UTC long window on one crypto pair.",
    ),
    "january-barometer": AcademicCatalogEntry(
        "january-barometer.py",
        "academic_ported.january_barometer.JanuaryBarometer",
        AcademicStatus.PARTIAL,
        reason="January signal on one equity; T-Bill switch omitted.",
    ),
    "low-volatility-factor-effect-in-stocks": AcademicCatalogEntry(
        "low-volatility-factor-effect-in-stocks.py",
        "academic_ported.low_volatility.LowVolatility",
        AcademicStatus.PARTIAL,
        reason="Vol-below-average filter; cross-sectional decile sort omitted.",
    ),
    "market-sentiment-and-an-overnight-anomaly": AcademicCatalogEntry(
        "market-sentiment-and-an-overnight-anomaly.py",
        "academic_ported.overnight_sentiment.OvernightSentiment",
        AcademicStatus.PARTIAL,
        reason="Price/VIX SMA filter; BMS data and MOC/MOO execution omitted.",
    ),
    "momentum-and-reversal-combined-with-volatility-effect-in-stocks": AcademicCatalogEntry(
        "momentum-and-reversal-combined-with-volatility-effect-in-stocks.py",
        "academic_ported.momentum_volatility.MomentumVolatility",
        AcademicStatus.PARTIAL,
        reason="High-vol momentum on one symbol; quintile portfolio omitted.",
    ),
    "momentum-effect-in-commodities": AcademicCatalogEntry(
        "momentum-effect-in-commodities.py",
        "academic_ported.commodity_momentum.CommodityMomentum",
        AcademicStatus.PARTIAL,
        reason="12-month ROC on one contract; quintile basket omitted.",
    ),
    "momentum-factor-and-style-rotation-effect": AcademicCatalogEntry(
        "momentum-factor-and-style-rotation-effect.py",
        "academic_ported.style_rotation.StyleRotation",
        AcademicStatus.PARTIAL,
        reason="12m ROC on one style ETF; winner/loser long/short omitted.",
    ),
    "momentum-factor-effect-in-stocks": AcademicCatalogEntry(
        "momentum-factor-effect-in-stocks.py",
        "academic_ported.cross_sectional_momentum.CrossSectionalMomentum",
        AcademicStatus.PARTIAL,
        reason="12-1 month UMD on one symbol; quantile long/short omitted.",
    ),
    "option-expiration-week-effect": AcademicCatalogEntry(
        "option-expiration-week-effect.py",
        "academic_ported.option_expiration_week.OptionExpirationWeek",
        AcademicStatus.PORTED,
        reason="Third-Friday week calendar hold on one index.",
    ),
    "paired-switching": AcademicCatalogEntry(
        "paired-switching.py",
        "academic_ported.paired_switching.PairedSwitching",
        AcademicStatus.PARTIAL,
        reason="Quarterly momentum on one symbol; dual-fund rotation omitted.",
    ),
    "pairs-trading-with-country-etfs": AcademicCatalogEntry(
        "pairs-trading-with-country-etfs.py",
        "academic_ported.country_etf_pairs.CountryEtfPairs",
        AcademicStatus.PARTIAL,
        reason="Two-leg z-score spread; pair selection and hold window omitted.",
    ),
    "payday-anomaly": AcademicCatalogEntry(
        "payday-anomaly.py",
        "academic_ported.payday_anomaly.PaydayAnomaly",
        AcademicStatus.PORTED,
        reason="Mid-month calendar entry on one index.",
    ),
    "residual-momentum-factor": AcademicCatalogEntry(
        "residual-momentum-factor.py",
        "academic_ported.residual_momentum.ResidualMomentum",
        AcademicStatus.PARTIAL,
        reason="Beta-adjusted momentum on one symbol; Fama-French deciles omitted.",
    ),
    "return-asymmetry-effect-in-commodity-futures": AcademicCatalogEntry(
        "return-asymmetry-effect-in-commodity-futures.py",
        "academic_ported.return_asymmetry.ReturnAsymmetry",
        AcademicStatus.PARTIAL,
        reason="IE asymmetry on one contract; cross-sectional rank omitted.",
    ),
    "sector-momentum-rotational-system": AcademicCatalogEntry(
        "sector-momentum-rotational-system.py",
        "academic_ported.sector_momentum.SectorMomentum",
        AcademicStatus.PARTIAL,
        reason="12m ROC on one sector ETF; top-3 rotation omitted.",
    ),
    "short-term-reversal-in-stocks": AcademicCatalogEntry(
        "short-term-reversal-in-stocks.py",
        "academic_ported.short_term_reversal.ShortTermReversal",
        AcademicStatus.PARTIAL,
        reason="Weekly reversal entry on one symbol; long/short basket omitted.",
    ),
    "short-term-reversal-with-futures": AcademicCatalogEntry(
        "short-term-reversal-with-futures.py",
        "academic_ported.weekly_reversal.WeeklyReversal",
        AcademicStatus.PARTIAL,
        reason="Weekly reversal on one contract; volume/OI filters omitted.",
    ),
    "skewness-effect-in-commodities": AcademicCatalogEntry(
        "skewness-effect-in-commodities.py",
        "academic_ported.skewness_effect.SkewnessEffect",
        AcademicStatus.PARTIAL,
        reason="Low-skewness long filter; quintile long/short omitted.",
    ),
    "term-structure-effect-in-commodities": AcademicCatalogEntry(
        "term-structure-effect-in-commodities.py",
        "academic_ported.term_structure_proxy.TermStructureProxy",
        AcademicStatus.PARTIAL,
        reason="60d momentum roll-return proxy; near/far contract data omitted.",
    ),
    "time-series-momentum-effect": AcademicCatalogEntry(
        "time-series-momentum-effect.py",
        "academic_ported.time_series_momentum.TimeSeriesMomentum",
        AcademicStatus.PARTIAL,
        reason="ROC sign plus vol cap on one asset; multi-asset vol-targeting omitted.",
    ),
    "trading-wti-brent-spread": AcademicCatalogEntry(
        "trading-wti-brent-spread.py",
        "academic_ported.wti_brent_spread.WtiBrentSpread",
        AcademicStatus.PARTIAL,
        reason="Two-leg WTI–Brent spread mean reversion.",
    ),
    "turn-of-the-month-in-equity-indexes": AcademicCatalogEntry(
        "turn-of-the-month-in-equity-indexes.py",
        "academic_ported.turn_of_the_month.TurnOfTheMonth",
        AcademicStatus.PORTED,
        reason="Calendar turn-of-month on one index.",
    ),
    "value-book-to-market-factor": AcademicCatalogEntry(
        "value-book-to-market-factor.py",
        "academic_ported.value_proxy.ValueProxy",
        AcademicStatus.PARTIAL,
        reason="Price-below-SMA value proxy; P/B universe sort omitted.",
    ),
    "volatility-risk-premium-effect": AcademicCatalogEntry(
        "volatility-risk-premium-effect.py",
        "academic_ported.vol_risk_premium.VolRiskPremium",
        AcademicStatus.PARTIAL,
        reason="Low realized-vol equity proxy; options straddle leg omitted.",
    ),
}


def _build_catalog() -> dict[str, AcademicCatalogEntry]:
    catalog: dict[str, AcademicCatalogEntry] = {}
    for name in _UPSTREAM_FILES:
        if name in _OVERRIDES:
            catalog[name] = _OVERRIDES[name]
        else:
            catalog[name] = AcademicCatalogEntry(
                f"{name}.py", None, AcademicStatus.BLOCKED, reason=_BLOCK_REASON,
            )
    return catalog


ACADEMIC_STRATEGY_CATALOG: dict[str, AcademicCatalogEntry] = _build_catalog()
