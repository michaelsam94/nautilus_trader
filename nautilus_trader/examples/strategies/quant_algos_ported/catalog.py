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

"""Catalog for Astralchemist/Quant-Algos strategy scaffolds."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class QaStatus(StrEnum):
    BLOCKED = "blocked"
    DEDUP_SKIP = "dedup_skip"


@dataclass(frozen=True)
class QaCatalogEntry:
    source_folder: str
    status: QaStatus
    dedup_target: str | None = None
    reason: str = ""


# Inspected 2026-07-06: strategy.py files are placeholder scaffolds (no signal logic).
QUANT_ALGOS_CATALOG: dict[str, QaCatalogEntry] = {
    "momentum/ma_cross": QaCatalogEntry(
        "momentum/ma_cross", QaStatus.DEDUP_SKIP,
        dedup_target="freqtrade_ported.average_strategy.AverageStrategy",
    ),
    "momentum/macd_oscillator": QaCatalogEntry(
        "momentum/macd_oscillator", QaStatus.DEDUP_SKIP,
        dedup_target="freqtrade_ported.macd_strategy.MacdStrategy",
    ),
    "momentum/awesome_oscillator": QaCatalogEntry(
        "momentum/awesome_oscillator", QaStatus.DEDUP_SKIP,
        dedup_target="freqtrade_ported.awesome_macd.AwesomeMacd",
    ),
    "momentum/dual_momentum": QaCatalogEntry(
        "momentum/dual_momentum", QaStatus.DEDUP_SKIP,
        dedup_target="vectorbt_ported.dual_momentum_etfs.DualMomentumEtfRotation",
    ),
    "mean_reversion/bollinger_bands_reversion": QaCatalogEntry(
        "mean_reversion/bollinger_bands_reversion", QaStatus.DEDUP_SKIP,
        dedup_target="freqtrade_ported.bband_rsi.BbandRsi",
    ),
    "mean_reversion/pairs_trading_statistical": QaCatalogEntry(
        "mean_reversion/pairs_trading_statistical", QaStatus.DEDUP_SKIP,
        dedup_target="systematic_trading_ported.pair_trading.PairTrading",
    ),
    "options/*": QaCatalogEntry(
        "options", QaStatus.BLOCKED, reason="Options runtime; out of scope.",
    ),
    "experimental/*": QaCatalogEntry(
        "experimental", QaStatus.BLOCKED, reason="GA/NAS optimizers; generator-only.",
    ),
}
