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
Catalog of leosmigel/analyzingalpha ports (via wangzhe3224/awesome-systematic-trading).

Also records the dedup verdict for chrisconlan/algorithmic-trading-with-python,
the other portable strategy source linked from the same awesome list.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AaStatus(StrEnum):
    PORTED = "ported"
    DEDUP_SKIP = "dedup_skip"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class AaCatalogEntry:
    source: str
    nautilus_module: str | None
    status: AaStatus
    dedup_target: str | None = None
    reason: str = ""


ANALYZINGALPHA_STRATEGY_CATALOG: dict[str, AaCatalogEntry] = {
    # --- Ported -------------------------------------------------------------
    "connors_rsi": AaCatalogEntry(
        "2019-09-26 backtrader-conners-rsi-strategy.py",
        "analyzingalpha_ported.connors_rsi.ConnorsRsi", AaStatus.PORTED,
        reason="Composite RSI+streak+percent-rank; source streak-RSI bug fixed.",
    ),
    "price_shear": AaCatalogEntry(
        "2021-09-23 crypto-price-shear notebook",
        "analyzingalpha_ported.price_shear.PriceShear", AaStatus.PORTED,
        reason="2.5x ATR displacement below EMA12, one-bar hold.",
    ),
    "slingshot": AaCatalogEntry(
        "2021-12-31 scot1and-slingshot notebook",
        "analyzingalpha_ported.slingshot.Slingshot", AaStatus.PORTED,
        reason="Daily trend+pullback with intraday EMA4-of-highs trigger, R-multiple exits.",
    ),
    # --- Dedup skipped -------------------------------------------------------
    "sma_crossover": AaCatalogEntry(
        "intrinio a-quant-quickstart crossover-strategy.py", None, AaStatus.DEDUP_SKIP,
        dedup_target="ema_cross.EMACross / freqtrade_ported.average_strategy.AverageStrategy",
    ),
    "rsi_threshold": AaCatalogEntry(
        "intrinio rsi-strategy.py + rsi-mean-reversion-strategy.py", None, AaStatus.DEDUP_SKIP,
        dedup_target="vectorbt_ported.rsi_threshold.RsiThreshold",
    ),
    "backtrader_dma": AaCatalogEntry(
        "2019-09-26 backtrader-dma-strategy.py", None, AaStatus.DEDUP_SKIP,
        dedup_target="freqtrade_ported.average_strategy.AverageStrategy",
    ),
    "backtrader_donchian": AaCatalogEntry(
        "2019-09-26 backtrader-donchain-strategy.py", None, AaStatus.DEDUP_SKIP,
        dedup_target="vectorbt_ported.donchian_breakout.DonchianBreakout",
    ),
    "conlan_macd_signal": AaCatalogEntry(
        "chrisconlan pypm/signals.py create_macd_signal (EMA 5/34 zero-cross)", None,
        AaStatus.DEDUP_SKIP,
        dedup_target="ema_cross.EMACross",
        reason="MACD oscillator sign flip == EMA5/34 crossover.",
    ),
    "conlan_bollinger_signal": AaCatalogEntry(
        "chrisconlan pypm/signals.py create_bollinger_band_signal", None, AaStatus.DEDUP_SKIP,
        dedup_target="bb_mean_reversion.BBMeanReversion",
    ),
    # --- Blocked --------------------------------------------------------------
    "sector_rsi": AaCatalogEntry(
        "2020-10-09 sector-rsi-strategy.py", None, AaStatus.BLOCKED,
        reason="Multi-asset sector rotation; needs a universe of instruments.",
    ),
    "value_strategy": AaCatalogEntry(
        "intrinio a-quant-quickstart-5 value-strategy.py", None, AaStatus.BLOCKED,
        reason="Fundamental (EV/EBITDA) screen; no fundamental data feed.",
    ),
    "pattern_recognition": AaCatalogEntry(
        "2020-04-18 algorithmic-chart-pattern-detection", None, AaStatus.BLOCKED,
        reason="scipy argrelextrema chart patterns; research script, look-ahead prone.",
    ),
    "conlan_ml_portfolio": AaCatalogEntry(
        "chrisconlan pypm/ml_model + portfolio optimization", None, AaStatus.BLOCKED,
        reason="ML feature/label pipeline and portfolio weight optimization, not bar signals.",
    ),
    "tutorials_infra": AaCatalogEntry(
        "API clients, data plumbing, notebook tutorials (~25 folders)", None, AaStatus.BLOCKED,
        reason="Not strategies (FTX/Binance/FRED/yfinance/SQL/OpenAI tutorials).",
    ),
}
