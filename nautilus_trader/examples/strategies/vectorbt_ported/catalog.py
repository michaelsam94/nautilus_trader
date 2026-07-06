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

"""Catalog of vectorbt-backtesting-skills template ports."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class VbtStatus(StrEnum):
    PORTED = "ported"
    PARTIAL = "partial"
    DEDUP_SKIP = "dedup_skip"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class VbtCatalogEntry:
    template_folder: str
    nautilus_module: str | None
    status: VbtStatus
    dedup_target: str | None = None
    reason: str = ""


VECTORBT_STRATEGY_CATALOG: dict[str, VbtCatalogEntry] = {
    "donchian": VbtCatalogEntry(
        "donchian", "vectorbt_ported.donchian_breakout.DonchianBreakout", VbtStatus.PORTED,
    ),
    "rsi": VbtCatalogEntry(
        "rsi", "vectorbt_ported.rsi_threshold.RsiThreshold", VbtStatus.PORTED,
        reason="RSI threshold only; distinct from BbandRsi.",
    ),
    "supertrend": VbtCatalogEntry(
        "supertrend", "vectorbt_ported.supertrend.SupertrendCross", VbtStatus.PORTED,
        reason="Session time filters omitted.",
    ),
    "momentum": VbtCatalogEntry(
        "momentum", "vectorbt_ported.double_momentum.DoubleMomentum", VbtStatus.PORTED,
        reason="Next-bar high breakout fill simplified.",
    ),
    "ema_crossover": VbtCatalogEntry(
        "ema_crossover", None, VbtStatus.DEDUP_SKIP,
        dedup_target="freqtrade_ported.average_strategy.AverageStrategy",
    ),
    "macd": VbtCatalogEntry(
        "macd", None, VbtStatus.DEDUP_SKIP,
        dedup_target="freqtrade_ported.macd_strategy.MacdStrategy",
    ),
    "dual_momentum": VbtCatalogEntry(
        "dual_momentum",
        "vectorbt_ported.dual_momentum_etfs.DualMomentumEtfRotation",
        VbtStatus.PORTED,
        reason="Quarterly ETF rotation; single-asset ROC in dual_momentum_rotation.",
    ),
    "buy_hold": VbtCatalogEntry(
        "buy_hold",
        "vectorbt_ported.buy_hold.BuyHoldBenchmark",
        VbtStatus.PORTED,
        reason="Single-asset buy-and-hold reference; multi-ETF weights need portfolio runner.",
    ),
    "rsi_accumulation": VbtCatalogEntry(
        "rsi_accumulation",
        "vectorbt_ported.rsi_accumulation.RsiAccumulation",
        VbtStatus.PARTIAL,
        reason="Weekly NIFTY RSI + Friday schedule simplified to bar RSI slabs.",
    ),
    "sda2": VbtCatalogEntry(
        "sda2", "vectorbt_ported.sda2_trend.Sda2Trend", VbtStatus.PORTED,
    ),
}
