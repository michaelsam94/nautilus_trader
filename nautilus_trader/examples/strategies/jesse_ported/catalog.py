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

"""Catalog of jesse-ai/example-strategies ports."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class JesseStatus(StrEnum):
    PORTED = "ported"
    DEDUP_SKIP = "dedup_skip"
    BLOCKED = "blocked"
    PARTIAL = "partial"


@dataclass(frozen=True)
class JesseCatalogEntry:
    source_folder: str
    nautilus_module: str | None
    status: JesseStatus
    dedup_target: str | None = None
    reason: str = ""


JESSE_STRATEGY_CATALOG: dict[str, JesseCatalogEntry] = {
    "Donchian": JesseCatalogEntry(
        "Donchian", "jesse_ported.donchian_sma200.DonchianSma200", JesseStatus.PORTED,
    ),
    "RSI2": JesseCatalogEntry(
        "RSI2", "jesse_ported.rsi2.Rsi2", JesseStatus.PORTED,
        reason="Long-only subset of bi-directional Jesse source.",
    ),
    "MACD_EMA": JesseCatalogEntry(
        "MACD_EMA", "jesse_ported.macd_ema.MacdEma", JesseStatus.PORTED,
    ),
    "SimpleBollinger": JesseCatalogEntry(
        "SimpleBollinger", "jesse_ported.simple_bollinger.SimpleBollingerIchimoku",
        JesseStatus.PORTED,
        reason="BB uses HLC/3 vs Jesse HL2.",
    ),
    "TurtleRules": JesseCatalogEntry(
        "TurtleRules", "jesse_ported.turtle_rules.TurtleRulesLong", JesseStatus.PARTIAL,
        reason="Long-only S1; no pyramiding/ATR stops.",
    ),
    "TradingView_RSI": JesseCatalogEntry(
        "TradingView_RSI", "jesse_ported.tradingview_rsi.TradingViewRsi", JesseStatus.PORTED,
        reason="Jesse stop-loss/take-profit omitted.",
    ),
    "IFR2": JesseCatalogEntry(
        "IFR2", "jesse_ported.ifr2.Ifr2", JesseStatus.PARTIAL,
        reason="Hilbert trend-mode filter omitted.",
    ),
    "SMACrossover": JesseCatalogEntry(
        "SMACrossover", None, JesseStatus.DEDUP_SKIP,
        dedup_target="freqtrade_ported.average_strategy.AverageStrategy",
        reason="Fast/slow MA crossover equivalent.",
    ),
    "DUAL_THRUST": JesseCatalogEntry(
        "DUAL_THRUST", None, JesseStatus.DEDUP_SKIP,
        dedup_target="systematic_trading_ported.dual_thrust.DualThrust",
        reason="Dual Thrust already ported from quant-trading.",
    ),
    "MAGen": JesseCatalogEntry(
        "MAGen",
        "jesse_ported.magen_fixed.MaGenFixed",
        JesseStatus.PARTIAL,
        reason="Fixed default hyperparameters; genetic search omitted.",
    ),
    "KDJ": JesseCatalogEntry(
        "KDJ", "jesse_ported.kdj.Kdj", JesseStatus.PARTIAL,
        reason="Long-only; ATR stop-loss from Jesse source omitted.",
    ),
}
