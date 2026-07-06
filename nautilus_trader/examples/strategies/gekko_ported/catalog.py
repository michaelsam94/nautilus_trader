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
Catalog of xFFFFF/Gekko-Strategies ports (via SpiralDevelopment/Awesome-Crypto-Trading).

The source collection holds 612 JS files, but they collapse into the strategy
families below — the bulk are parameter variants, timestamped duplicates, or
neural-net/GA strategies that are not portable as bar logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class GekkoStatus(StrEnum):
    PORTED = "ported"
    DEDUP_SKIP = "dedup_skip"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class GekkoCatalogEntry:
    source_family: str
    nautilus_module: str | None
    status: GekkoStatus
    dedup_target: str | None = None
    reason: str = ""


GEKKO_STRATEGY_CATALOG: dict[str, GekkoCatalogEntry] = {
    # --- Ported -------------------------------------------------------------
    "RSI_BULL_BEAR": GekkoCatalogEntry(
        "RSI_BULL_BEAR", "gekko_ported.rsi_bull_bear.RsiBullBear", GekkoStatus.PORTED,
        reason="Regime-switched dual RSI (Tommie Hansen); the flagship Gekko strategy.",
    ),
    "RSI_BULL_BEAR_ADX": GekkoCatalogEntry(
        "RSI Bull and Bear - ADX modifier", "gekko_ported.rsi_bull_bear_adx.RsiBullBearAdx",
        GekkoStatus.PORTED,
        reason="ADX modifier applied as documented (original JS silently drops it).",
    ),
    "NEO": GekkoCatalogEntry(
        "NEO", "gekko_ported.neo.Neo", GekkoStatus.PORTED,
        reason="Triple-RSI with ROC idle-bull split.",
    ),
    "BodhiDI_public": GekkoCatalogEntry(
        "BodhiDI_public", "gekko_ported.bodhi_di.BodhiDi", GekkoStatus.PORTED,
        reason="Pure DI flipper; distinct from AdxMomentum (no ADX gate/momentum).",
    ),
    "buyatsellat": GekkoCatalogEntry(
        "buyatsellat / BuyAtSellAt / buyatsellat_ui", "gekko_ported.buy_at_sell_at.BuyAtSellAt",
        GekkoStatus.PORTED,
        reason="Mechanical percent flipper; advice-close anchored as in source.",
    ),
    # --- Dedup skipped -------------------------------------------------------
    "BBRSI": GekkoCatalogEntry(
        "BBRSI / n8_v2_BB_RSI_SL / Bro-RSI", None, GekkoStatus.DEDUP_SKIP,
        dedup_target="freqtrade_ported.bband_rsi.BbandRsi",
    ),
    "CCI": GekkoCatalogEntry(
        "CCI / custom_CCI", None, GekkoStatus.DEDUP_SKIP,
        dedup_target="freqtrade_ported.cci_strategy.CciStrategy",
    ),
    "MACD": GekkoCatalogEntry(
        "MACD_1520024643 / talib-macd variants", None, GekkoStatus.DEDUP_SKIP,
        dedup_target="freqtrade_ported.macd_strategy.MacdStrategy",
    ),
    "EMA_DEMA_TEMA_cross": GekkoCatalogEntry(
        "EMACrossover / DEMACrossover / DEMA MrGox / TEMA", None, GekkoStatus.DEDUP_SKIP,
        dedup_target="ema_cross.EMACross / freqtrade_ported.average_strategy.AverageStrategy",
    ),
    "SuperTrend": GekkoCatalogEntry(
        "SuperTrend / Supertrend_Gab0", None, GekkoStatus.DEDUP_SKIP,
        dedup_target="freqtrade_ported.supertrend.Supertrend",
    ),
    "Ichimoku": GekkoCatalogEntry(
        "Ichimoku (!WORKSOP)", None, GekkoStatus.DEDUP_SKIP,
        dedup_target="backtrader_ported.ichimoku_cloud.IchimokuCloudBreakout",
    ),
    "RSI_threshold_variants": GekkoCatalogEntry(
        "CUSTOM_RSI / x2_rsi / rsidyn / A1RSI / RsiStopLoss / MK_RSI_BULL_BEAR", None,
        GekkoStatus.DEDUP_SKIP,
        dedup_target="vectorbt_ported.rsi_threshold.RsiThreshold",
        reason="Threshold/param variants of ported RSI families.",
    ),
    "StochRSI_DI_combos": GekkoCatalogEntry(
        "Bro-StochRSI-ADX-DI / DI / ATR_ADX0", None, GekkoStatus.DEDUP_SKIP,
        dedup_target="gekko_ported.bodhi_di.BodhiDi",
        reason="DI-cross cores with extra gates; nearest ported ancestor kept.",
    ),
    # --- Blocked --------------------------------------------------------------
    "NeuralNet_family": GekkoCatalogEntry(
        "NeuralNet / NNv2 / neuralnet_v2 / neuralnet_zschro / Luke_NN / ManuNet / NN_ADX_RSI",
        None, GekkoStatus.BLOCKED,
        reason="Online neural nets (zero/convnet); not deterministic bar logic.",
    ),
    "GA_family": GekkoCatalogEntry(
        "mounirs-ga-version-1/2 / mounirs_esto", None, GekkoStatus.BLOCKED,
        reason="Genetic-algorithm parameter search harnesses, not strategies.",
    ),
    "ATR_ADX": GekkoCatalogEntry(
        "ATR_ADX / ATR_ADX_v2 / ATR_MA", None, GekkoStatus.BLOCKED,
        reason="Heikin-Ashi adaptive TradingView adaptation; deferred (large port).",
    ),
    "Misc_personal": GekkoCatalogEntry(
        "Dave / Kane2 / n8 / w2 / tether / scarface_v2 / bryanbeck / jazzbre / "
        "bestone_updated_hardcoded / CloggyStrats / TommieHansenStrategies / "
        "GekkoStrategies / AdoptedStrategies / FIXPRICE / DynBuySell / EMADIV / "
        "EMA_OR_PRICE_DIV / gekko-strat-hl / Neapticator / BitBankStrategy",
        None, GekkoStatus.BLOCKED,
        reason="Personal variant packs: param forks of ported families, exchange-"
               "specific hacks, or logs-only folders.",
    ),
}
