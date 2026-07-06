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
Catalog for awesome-systematic-trading linked alpha strategies.

Source list: https://github.com/wangzhe3224/awesome-systematic-trading
The list itself contains no strategy code — entries reference external repositories.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AstStatus(StrEnum):
    PORTED = "ported"
    PARTIAL = "partial"
    DEDUP_SKIP = "dedup_skip"
    BLOCKED = "blocked"
    EXTERNAL = "external"


@dataclass(frozen=True)
class AstCatalogEntry:
    awesome_section: str
    linked_repo: str
    status: AstStatus
    nautilus_module: str | None = None
    dedup_target: str | None = None
    reason: str = ""


# Alpha strategies from awesome-systematic-trading → je-suis-tm/quant-trading
AST_STRATEGY_CATALOG: dict[str, AstCatalogEntry] = {
    "quant-trading/Dual Thrust": AstCatalogEntry(
        "General Alpha", "je-suis-tm/quant-trading", AstStatus.PORTED,
        "systematic_trading_ported.dual_thrust.DualThrust",
    ),
    "quant-trading/London Breakout": AstCatalogEntry(
        "General Alpha", "je-suis-tm/quant-trading", AstStatus.PORTED,
        "systematic_trading_ported.london_breakout.LondonBreakout",
    ),
    "quant-trading/Parabolic SAR": AstCatalogEntry(
        "General Alpha", "je-suis-tm/quant-trading", AstStatus.PORTED,
        "systematic_trading_ported.parabolic_sar.ParabolicSarStrategy",
    ),
    "quant-trading/Heikin-Ashi Marubozu": AstCatalogEntry(
        "General Alpha", "je-suis-tm/quant-trading", AstStatus.PORTED,
        "systematic_trading_ported.heikin_ashi_marubozu.HeikinAshiMarubozu",
        dedup_target="freqtrade_ported.strategy001.Strategy001",
        reason="Different HA rules than Strategy001 EMA combo.",
    ),
    "quant-trading/Bollinger Bottom W": AstCatalogEntry(
        "General Alpha", "je-suis-tm/quant-trading", AstStatus.PORTED,
        "systematic_trading_ported.bollinger_bottom_w.BollingerBottomW",
        reason="Simplified W-pattern vs full five-node scan in source.",
    ),
    "quant-trading/MACD Oscillator": AstCatalogEntry(
        "General Alpha", "je-suis-tm/quant-trading", AstStatus.DEDUP_SKIP,
        dedup_target="freqtrade_ported.average_strategy.AverageStrategy",
        reason="Fast/slow MA crossover equivalent.",
    ),
    "quant-trading/Awesome Oscillator": AstCatalogEntry(
        "General Alpha", "je-suis-tm/quant-trading", AstStatus.DEDUP_SKIP,
        dedup_target="freqtrade_ported.awesome_macd.AwesomeMacd",
        reason="AO momentum already covered.",
    ),
    "quant-trading/RSI Pattern Recognition": AstCatalogEntry(
        "General Alpha", "je-suis-tm/quant-trading", AstStatus.DEDUP_SKIP,
        dedup_target="freqtrade_ported.bband_rsi.BbandRsi",
        reason="RSI 30/70 overbought/oversold.",
    ),
    "quant-trading/Shooting Star": AstCatalogEntry(
        "General Alpha", "je-suis-tm/quant-trading", AstStatus.PORTED,
        "systematic_trading_ported.shooting_star_short.ShootingStarShort",
        reason="Short entry + ShootingStarExit long-only bearish exit variant.",
    ),
    "quant-trading/Pair Trading": AstCatalogEntry(
        "General Alpha", "je-suis-tm/quant-trading", AstStatus.PORTED,
        "systematic_trading_ported.pair_trading.PairTrading",
        reason="Two-leg z-score with simplified Engle-Granger residual gate.",
    ),
    "quant-trading/Options Straddle": AstCatalogEntry(
        "General Alpha", "je-suis-tm/quant-trading", AstStatus.BLOCKED,
        reason="Options strategy.",
    ),
    "quant-trading/VIX Calculator": AstCatalogEntry(
        "General Alpha", "je-suis-tm/quant-trading", AstStatus.BLOCKED,
        reason="Volatility index tool.",
    ),
    "quant-trading/Monte Carlo": AstCatalogEntry(
        "Quantamental", "je-suis-tm/quant-trading", AstStatus.BLOCKED,
        reason="Simulation project.",
    ),
    "quant-trading/Oil Money": AstCatalogEntry(
        "Quantamental", "je-suis-tm/quant-trading", AstStatus.BLOCKED,
        reason="Macro commodity analysis.",
    ),
    "quant-trading/Smart Farmers": AstCatalogEntry(
        "Quantamental", "je-suis-tm/quant-trading", AstStatus.BLOCKED,
        reason="Agricultural forecasting.",
    ),
    "analyzingalpha": AstCatalogEntry(
        "General Alpha", "leosmigel/analyzingalpha", AstStatus.BLOCKED,
        reason="Git LFS pointer stubs in clone; strategies not vendored as plain Python.",
    ),
    "Astralchemist/Quant-Algos": AstCatalogEntry(
        "General Alpha", "Astralchemist/Quant-Algos", AstStatus.BLOCKED,
        reason="Scaffold placeholders; see quant_algos_ported/catalog.py.",
    ),
    "ulandz/ai-trader": AstCatalogEntry(
        "General Alpha", "ulandz/ai-trader", AstStatus.EXTERNAL,
        reason="YAML-driven Backtrader pack; separate port track.",
    ),
    "PyTrendFollow": AstCatalogEntry(
        "General Alpha", "chrism2671/PyTrendFollow", AstStatus.EXTERNAL,
        reason="Futures trend-following framework; separate port effort.",
    ),
    "czsc": AstCatalogEntry(
        "General Alpha", "waditu/czsc", AstStatus.EXTERNAL,
        reason="Chan theory analysis library.",
    ),
    "fmzquant/strategies": AstCatalogEntry(
        "General Alpha", "fmzquant/strategies", AstStatus.EXTERNAL,
        reason="Chinese strategy collection; separate catalog needed.",
    ),
    "TrendRider (crypto_focus)": AstCatalogEntry(
        "Crypto", "darkvolg/trendrider-strategy", AstStatus.EXTERNAL,
        reason="Freqtrade strategy; see freqtrade_ported catalog.",
    ),
}


def catalog_summary() -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in AST_STRATEGY_CATALOG.values():
        counts[entry.status] = counts.get(entry.status, 0) + 1
    return counts
