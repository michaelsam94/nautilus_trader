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
Catalog of Freqtrade strategies from github.com/freqtrade/freqtrade-strategies.

Status values: ``ported``, ``partial``, ``blocked``, ``deprecated``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PortStatus(StrEnum):
    PORTED = "ported"
    PARTIAL = "partial"
    BLOCKED = "blocked"
    DEPRECATED = "deprecated"


@dataclass(frozen=True)
class StrategyCatalogEntry:
    source_path: str
    nautilus_module: str | None
    status: PortStatus
    reason: str = ""


# Total strategies in upstream repo (user_data/strategies/**/*.py): 65
FREQTRADE_STRATEGY_CATALOG: dict[str, StrategyCatalogEntry] = {
    # --- Ported (18) ---
    "BbandRsi": StrategyCatalogEntry(
        "berlinguyinca/BbandRsi.py", "bband_rsi.BbandRsi", PortStatus.PORTED,
    ),
    "Simple": StrategyCatalogEntry(
        "berlinguyinca/Simple.py", "simple_strategy.Simple", PortStatus.PORTED,
    ),
    "MACDStrategy": StrategyCatalogEntry(
        "berlinguyinca/MACDStrategy.py", "macd_strategy.MacdStrategy", PortStatus.PORTED,
    ),
    "MACDStrategy_crossed": StrategyCatalogEntry(
        "berlinguyinca/MACDStrategy_crossed.py",
        "macd_strategy_crossed.MacdStrategyCrossed",
        PortStatus.PORTED,
    ),
    "AverageStrategy": StrategyCatalogEntry(
        "berlinguyinca/AverageStrategy.py", "average_strategy.AverageStrategy", PortStatus.PORTED,
    ),
    "UniversalMACD": StrategyCatalogEntry(
        "UniversalMACD.py", "universal_macd.UniversalMacd", PortStatus.PORTED,
    ),
    "Low_BB": StrategyCatalogEntry(
        "berlinguyinca/Low_BB.py", "low_bb.LowBb", PortStatus.PARTIAL,
        "Exit uses trailing stop/ROI only in Freqtrade; not mapped.",
    ),
    "DoesNothingStrategy": StrategyCatalogEntry(
        "berlinguyinca/DoesNothingStrategy.py", "does_nothing.DoesNothing", PortStatus.PORTED,
    ),
    "Strategy001": StrategyCatalogEntry(
        "Strategy001.py", "strategy001.Strategy001", PortStatus.PORTED,
    ),
    "Diamond": StrategyCatalogEntry(
        "Diamond.py", "diamond.Diamond", PortStatus.PORTED,
    ),
    "hlhb": StrategyCatalogEntry("hlhb.py", "hlhb.Hlhb", PortStatus.PORTED),
    "AdxSmas": StrategyCatalogEntry(
        "berlinguyinca/AdxSmas.py", "adx_smas.AdxSmas", PortStatus.PORTED,
    ),
    "AwesomeMacd": StrategyCatalogEntry(
        "berlinguyinca/AwesomeMacd.py", "awesome_macd.AwesomeMacd", PortStatus.PORTED,
    ),
    "CMCWinner": StrategyCatalogEntry(
        "berlinguyinca/CMCWinner.py", "cmc_winner.CmcWinner", PortStatus.PORTED,
    ),
    "TechnicalExampleStrategy": StrategyCatalogEntry(
        "berlinguyinca/TechnicalExampleStrategy.py",
        "technical_example.TechnicalExample",
        PortStatus.PORTED,
    ),
    "Scalp": StrategyCatalogEntry("berlinguyinca/Scalp.py", "scalp.Scalp", PortStatus.PORTED),
    "Bandtastic": StrategyCatalogEntry(
        "Bandtastic.py", "bandtastic.Bandtastic", PortStatus.PARTIAL,
        "Hyperopt categorical BB bands simplified to std=1/2 defaults.",
    ),
    "ADXMomentum": StrategyCatalogEntry(
        "berlinguyinca/ADXMomentum.py", "adx_momentum.AdxMomentum", PortStatus.PARTIAL,
        "Parabolic SAR from original not used in entry/exit logic.",
    ),
    # --- Blocked: multi-timeframe / informative pairs ---
    "MultiRSI": StrategyCatalogEntry(
        "berlinguyinca/MultiRSI.py", None, PortStatus.BLOCKED,
        "Requires resample_to_interval / resampled_merge (multi-timeframe).",
    ),
    "ReinforcedAverageStrategy": StrategyCatalogEntry(
        "berlinguyinca/ReinforcedAverageStrategy.py", None, PortStatus.BLOCKED,
        "Requires higher-timeframe SMA merge.",
    ),
    "CCIStrategy": StrategyCatalogEntry(
        "berlinguyinca/CCIStrategy.py", None, PortStatus.BLOCKED,
        "Custom resample() with interpolated higher TF columns.",
    ),
    "multi_tf": StrategyCatalogEntry(
        "multi_tf.py", None, PortStatus.BLOCKED, "Multi-timeframe informative pairs.",
    ),
    "InformativeSample": StrategyCatalogEntry(
        "InformativeSample.py", None, PortStatus.BLOCKED, "Informative pair pattern.",
    ),
    "mabStra": StrategyCatalogEntry(
        "mabStra.py", None, PortStatus.BLOCKED, "Complex multi-indicator / pandas_ta.",
    ),
    # --- Blocked: futures / short / leverage ---
    "FAdxSmaStrategy": StrategyCatalogEntry(
        "futures/FAdxSmaStrategy.py", None, PortStatus.BLOCKED, "Futures-only strategy.",
    ),
    "FOttStrategy": StrategyCatalogEntry(
        "futures/FOttStrategy.py", None, PortStatus.BLOCKED, "Futures OTT strategy.",
    ),
    "FReinforcedStrategy": StrategyCatalogEntry(
        "futures/FReinforcedStrategy.py", None, PortStatus.BLOCKED, "Futures reinforced.",
    ),
    "FSampleStrategy": StrategyCatalogEntry(
        "futures/FSampleStrategy.py", None, PortStatus.BLOCKED, "Futures sample.",
    ),
    "FSupertrendStrategy": StrategyCatalogEntry(
        "futures/FSupertrendStrategy.py", None, PortStatus.BLOCKED, "Futures supertrend.",
    ),
    "TrendFollowingStrategy": StrategyCatalogEntry(
        "futures/TrendFollowingStrategy.py", None, PortStatus.BLOCKED, "Futures trend.",
    ),
    "VolatilitySystem": StrategyCatalogEntry(
        "futures/VolatilitySystem.py", None, PortStatus.BLOCKED, "Futures volatility system.",
    ),
    # --- Blocked: lookahead bias (educational) ---
    "DevilStra": StrategyCatalogEntry(
        "lookahead_bias/DevilStra.py", None, PortStatus.DEPRECATED,
        "Documented lookahead bias example — do not port.",
    ),
    "GodStraNew": StrategyCatalogEntry(
        "lookahead_bias/GodStraNew.py", None, PortStatus.DEPRECATED,
        "Lookahead bias example.",
    ),
    "Zeus": StrategyCatalogEntry(
        "lookahead_bias/Zeus.py", None, PortStatus.DEPRECATED, "Lookahead bias example.",
    ),
    "wtc": StrategyCatalogEntry(
        "lookahead_bias/wtc.py", None, PortStatus.DEPRECATED, "Lookahead bias example.",
    ),
    # --- Blocked: custom stoploss / callbacks ---
    "CustomStoplossWithPSAR": StrategyCatalogEntry(
        "CustomStoplossWithPSAR.py", None, PortStatus.BLOCKED,
        "Uses custom_stoploss() callback with PSAR.",
    ),
    "FixedRiskRewardLoss": StrategyCatalogEntry(
        "FixedRiskRewardLoss.py", None, PortStatus.BLOCKED,
        "Uses custom_stoploss() for R:R.",
    ),
    "BreakEven": StrategyCatalogEntry(
        "BreakEven.py", None, PortStatus.BLOCKED, "Custom stoploss / break-even logic.",
    ),
    # --- Blocked: heavy / niche dependencies ---
    "Supertrend": StrategyCatalogEntry(
        "Supertrend.py", None, PortStatus.BLOCKED,
        "Custom numpy supertrend; 6 hyperopt params per side.",
    ),
    "GodStra": StrategyCatalogEntry(
        "GodStra.py", None, PortStatus.BLOCKED, "Genetic / hyperopt mega-strategy.",
    ),
    "Heracles": StrategyCatalogEntry(
        "Heracles.py", None, PortStatus.BLOCKED, "Complex multi-condition strategy.",
    ),
    "PatternRecognition": StrategyCatalogEntry(
        "PatternRecognition.py", None, PortStatus.BLOCKED, "CDL candlestick patterns (TALib).",
    ),
    "TDSequentialStrategy": StrategyCatalogEntry(
        "berlinguyinca/TDSequentialStrategy.py", None, PortStatus.BLOCKED,
        "TD Sequential — no native indicator.",
    ),
    "BinHV27": StrategyCatalogEntry(
        "berlinguyinca/BinHV27.py", None, PortStatus.BLOCKED,
        "Complex ADX/DI state machine.",
    ),
    "BinHV45": StrategyCatalogEntry(
        "berlinguyinca/BinHV45.py", None, PortStatus.BLOCKED,
        "Complex ADX/DI state machine.",
    ),
    "ClucMay72018": StrategyCatalogEntry(
        "berlinguyinca/ClucMay72018.py", None, PortStatus.BLOCKED, "Multi-filter scalp.",
    ),
    "CombinedBinHAndCluc": StrategyCatalogEntry(
        "berlinguyinca/CombinedBinHAndCluc.py", None, PortStatus.BLOCKED, "Combined filters.",
    ),
    "CofiBitStrategy": StrategyCatalogEntry(
        "berlinguyinca/CofiBitStrategy.py", None, PortStatus.BLOCKED, "Custom cofi indicator.",
    ),
    "EMASkipPump": StrategyCatalogEntry(
        "berlinguyinca/EMASkipPump.py", None, PortStatus.BLOCKED, "Pump detection logic.",
    ),
    "SmoothOperator": StrategyCatalogEntry(
        "berlinguyinca/SmoothOperator.py", None, PortStatus.BLOCKED,
        "Author notes 'DO NOT USE'; heavy smoothing.",
    ),
    "SmoothScalp": StrategyCatalogEntry(
        "berlinguyinca/SmoothScalp.py", None, PortStatus.BLOCKED, "MFI + ADX scalp variant.",
    ),
    "ReinforcedQuickie": StrategyCatalogEntry(
        "berlinguyinca/ReinforcedQuickie.py", None, PortStatus.BLOCKED, "Multi-TF reinforcement.",
    ),
    "ReinforcedSmoothScalp": StrategyCatalogEntry(
        "berlinguyinca/ReinforcedSmoothScalp.py", None, PortStatus.BLOCKED, "Multi-TF scalp.",
    ),
    "Quickie": StrategyCatalogEntry(
        "berlinguyinca/Quickie.py", None, PortStatus.BLOCKED, "TEMA + ADX — TEMA not ported.",
    ),
    "Strategy002": StrategyCatalogEntry(
        "Strategy002.py", None, PortStatus.BLOCKED, "CDLHAMMER + Fisher RSI + SAR.",
    ),
    "Strategy003": StrategyCatalogEntry(
        "Strategy003.py", None, PortStatus.BLOCKED, "MFI + Fisher + many filters.",
    ),
    "Strategy004": StrategyCatalogEntry(
        "Strategy004.py", None, PortStatus.BLOCKED, "Dual STOCHF + volume rolling.",
    ),
    "Strategy005": StrategyCatalogEntry(
        "Strategy005.py", None, PortStatus.BLOCKED, "Hyperopt categorical sell trigger.",
    ),
    "Strategy001_custom_exit": StrategyCatalogEntry(
        "Strategy001_custom_exit.py", None, PortStatus.BLOCKED, "Custom exit callback.",
    ),
    "PowerTower": StrategyCatalogEntry(
        "PowerTower.py", None, PortStatus.BLOCKED, "Custom Power Tower indicator.",
    ),
    "MultiMa": StrategyCatalogEntry(
        "MultiMa.py", None, PortStatus.BLOCKED, "Multiple MA hyperopt grid.",
    ),
    "HourBasedStrategy": StrategyCatalogEntry(
        "HourBasedStrategy.py", None, PortStatus.BLOCKED, "Time-of-day filters.",
    ),
    "SwingHighToSky": StrategyCatalogEntry(
        "SwingHighToSky.py", None, PortStatus.BLOCKED, "Swing high detection.",
    ),
    "TrendRiderStrategy": StrategyCatalogEntry(
        "TrendRiderStrategy.py", None, PortStatus.BLOCKED, "Complex trend rider.",
    ),
    "Freqtrade_backtest_validation_freqtrade1": StrategyCatalogEntry(
        "berlinguyinca/Freqtrade_backtest_validation_freqtrade1.py",
        None,
        PortStatus.DEPRECATED,
        "Validation harness, not a trading strategy.",
    ),
    "ASDTSRockwellTrading": StrategyCatalogEntry(
        "berlinguyinca/ASDTSRockwellTrading.py", None, PortStatus.BLOCKED,
        "Niche ASDTS indicator.",
    ),
}


def catalog_summary() -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in FREQTRADE_STRATEGY_CATALOG.values():
        counts[entry.status] = counts.get(entry.status, 0) + 1
    return counts
