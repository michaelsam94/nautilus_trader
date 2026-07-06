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

"""Catalog of ali-azary Backtrader strategy ports."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class BtStatus(StrEnum):
    PORTED = "ported"
    PARTIAL = "partial"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class BtCatalogEntry:
    source_file: str
    nautilus_module: str | None
    status: BtStatus
    reason: str = ""


BACKTRADER_STRATEGY_CATALOG: dict[str, BtCatalogEntry] = {
    "KeltnerBreakoutStrategy": BtCatalogEntry(
        "KeltnerBreakoutStrategy.py",
        "backtrader_ported.keltner_breakout.KeltnerBreakout",
        BtStatus.PORTED,
        reason="Long-only; ATR trailing stop added.",
    ),
    "RelativeMomentumAccel": BtCatalogEntry(
        "RelativeMomentumAccel.py",
        "backtrader_ported.relative_momentum_accel.RelativeMomentumAccel",
        BtStatus.PARTIAL,
        reason="ATR trailing stop simplified to mean exit.",
    ),
    "MomentumIgnitionStrategy": BtCatalogEntry(
        "MomentumIgnitionStrategy.py",
        "backtrader_ported.momentum_ignition.MomentumIgnition",
        BtStatus.PARTIAL,
        reason="Long-only; ATR stop omitted.",
    ),
    "KeltnerChannelRSIBreakoutStrategy": BtCatalogEntry(
        "KeltnerChannelRSIBreakoutStrategy.py",
        "backtrader_ported.keltner_rsi_breakout.KeltnerRsiBreakout",
        BtStatus.PARTIAL,
        reason="Long-only; short leg and bi-directional trailing omitted.",
    ),
    "IchimokuCloudStrategy": BtCatalogEntry(
        "IchimokuCloudStrategy.py",
        "backtrader_ported.ichimoku_cloud.IchimokuCloudBreakout",
        BtStatus.PORTED,
        reason="Long-only; high-based percent trailing stop.",
    ),
    "MLEnhancedADXStrategy": BtCatalogEntry(
        "MLEnhancedADXStrategy.py",
        "backtrader_ported.ml_enhanced_adx.MlEnhancedAdx",
        BtStatus.PARTIAL,
        reason="8-feature rule score; RandomForest training omitted.",
    ),
    "OBVMarketRegimeStrategyBreakout": BtCatalogEntry(
        "OBVMarketRegimeStrategyBreakout.py",
        "backtrader_ported.obv_market_regime_breakout.ObvMarketRegimeBreakout",
        BtStatus.PARTIAL,
        reason="Long-only; trailing stop omitted.",
    ),
    "OBVmomentumStrategy": BtCatalogEntry(
        "OBVmomentumStrategy.py",
        "backtrader_ported.obv_momentum.ObvMomentum",
        BtStatus.PARTIAL,
        reason="Long-only; trailing stop omitted.",
    ),
    "OUMeanReversionStrategy": BtCatalogEntry(
        "OUMeanReversionStrategy.py",
        "backtrader_ported.ou_mean_reversion.OuMeanReversion",
        BtStatus.PARTIAL,
        reason="Long-only subset of bi-directional OU z-score logic.",
    ),
    "QuantileChannelStrategy": BtCatalogEntry(
        "QuantileChannelStrategy.py",
        "backtrader_ported.quantile_channel.QuantileChannelBreakout",
        BtStatus.PARTIAL,
        reason="Rolling quantile bands; scipy L-BFGS optimizer omitted.",
    ),
    "RegimeFilteredTrendStrategy": BtCatalogEntry(
        "RegimeFilteredTrendStrategy.py",
        "backtrader_ported.regime_filtered_trend.RegimeFilteredTrend",
        BtStatus.PARTIAL,
        reason="Regime ATR trail added; short leg and variable sizing omitted.",
    ),
}
