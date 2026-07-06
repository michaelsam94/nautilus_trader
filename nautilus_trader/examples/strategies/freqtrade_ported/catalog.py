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
    # --- Ported / partial (61 entries: 52 ported + 9 partial) ---
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
        "Exit uses trailing stop/ROI only in Freqtrade; no exit signal ported.",
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
        "Bandtastic.py", "bandtastic.Bandtastic", PortStatus.PORTED,
        "Hyperopt categorical BB bands fixed to hyperopt defaults.",
    ),
    "ADXMomentum": StrategyCatalogEntry(
        "berlinguyinca/ADXMomentum.py", "adx_momentum.AdxMomentum", PortStatus.PORTED,
    ),
    "HourBasedStrategy": StrategyCatalogEntry(
        "HourBasedStrategy.py", "hour_based.HourBased", PortStatus.PORTED,
        "Time-of-day filter; 1h bars recommended.",
    ),
    "SwingHighToSky": StrategyCatalogEntry(
        "SwingHighToSky.py", "swing_high_to_sky.SwingHighToSky", PortStatus.PORTED,
    ),
    "MultiMa": StrategyCatalogEntry(
        "MultiMa.py", "multi_ma.MultiMa", PortStatus.PORTED,
        "TEMA stack; long warmup for sell_ma_gap=68.",
    ),
    "PowerTower": StrategyCatalogEntry(
        "PowerTower.py", "power_tower.PowerTower", PortStatus.PORTED,
    ),
    "Quickie": StrategyCatalogEntry(
        "berlinguyinca/Quickie.py", "quickie.Quickie", PortStatus.PORTED,
    ),
    "SmoothScalp": StrategyCatalogEntry(
        "berlinguyinca/SmoothScalp.py", "smooth_scalp.SmoothScalp", PortStatus.PORTED,
    ),
    "Supertrend": StrategyCatalogEntry(
        "Supertrend.py", "supertrend.Supertrend", PortStatus.PORTED,
        "Hyperopt params fixed to upstream buy_params/sell_params defaults.",
    ),
    "ClucMay72018": StrategyCatalogEntry(
        "berlinguyinca/ClucMay72018.py", "cluc_may72018.ClucMay72018", PortStatus.PORTED,
    ),
    "Strategy002": StrategyCatalogEntry(
        "Strategy002.py", "strategy002.Strategy002", PortStatus.PORTED,
        "CDLHAMMER approximated; Fisher RSI + SAR exit mapped.",
    ),
    "Strategy003": StrategyCatalogEntry(
        "Strategy003.py", "strategy003.Strategy003", PortStatus.PORTED,
    ),
    "Strategy004": StrategyCatalogEntry(
        "Strategy004.py", "strategy004.Strategy004", PortStatus.PORTED,
    ),
    "Strategy005": StrategyCatalogEntry(
        "Strategy005.py", "strategy005.Strategy005", PortStatus.PORTED,
        "sell_trigger fixed to hyperopt default rsi-macd-minusdi.",
    ),
    "MultiRSI": StrategyCatalogEntry(
        "berlinguyinca/MultiRSI.py", "multi_rsi.MultiRsi", PortStatus.PORTED,
        "Requires informative_bar_types for 2x/8x bar types.",
    ),
    "InformativeSample": StrategyCatalogEntry(
        "InformativeSample.py", "informative_sample.InformativeSample", PortStatus.PORTED,
        "Requires informative_bar_type for reference pair (e.g. BTC 15m).",
    ),
    "ReinforcedQuickie": StrategyCatalogEntry(
        "berlinguyinca/ReinforcedQuickie.py",
        "reinforced_quickie.ReinforcedQuickie",
        PortStatus.PORTED,
        "60m resample_sma via trend_bar_type subscription.",
    ),
    "BreakEven": StrategyCatalogEntry(
        "BreakEven.py", "break_even.BreakEven", PortStatus.PORTED,
        "ROI table mapped to min_profit_to_exit; never enters.",
    ),
    "CustomStoplossWithPSAR": StrategyCatalogEntry(
        "CustomStoplossWithPSAR.py",
        "custom_stoploss_psar.CustomStoplossWithPsar",
        PortStatus.PORTED,
        "PSAR trailing stop via check_custom_stoploss.",
    ),
    "FixedRiskRewardLoss": StrategyCatalogEntry(
        "FixedRiskRewardLoss.py",
        "fixed_risk_reward_loss.FixedRiskRewardLoss",
        PortStatus.PORTED,
        "ATR stop/R:R managed in on_bar; always-enter placeholder preserved.",
    ),
    "PatternRecognition": StrategyCatalogEntry(
        "PatternRecognition.py",
        "pattern_recognition.PatternRecognition",
        PortStatus.PORTED,
        "CDLHAMMER and CDLHIGHWAVE implemented; other TALib patterns omitted.",
    ),
    "FSupertrendStrategy": StrategyCatalogEntry(
        "futures/FSupertrendStrategy.py",
        "f_supertrend.FSupertrend",
        PortStatus.PORTED,
        "Long/short via FreqtradeLongShortStrategy; needs short-capable account.",
    ),
    "ReinforcedAverageStrategy": StrategyCatalogEntry(
        "berlinguyinca/ReinforcedAverageStrategy.py",
        "reinforced_average.ReinforcedAverage",
        PortStatus.PORTED,
        "Higher-TF SMA via trend_bar_type.",
    ),
    "CCIStrategy": StrategyCatalogEntry(
        "berlinguyinca/CCIStrategy.py",
        "cci_strategy.CciStrategy",
        PortStatus.PORTED,
        "5x resample SMAs via resample_bar_type.",
    ),
    "multi_tf": StrategyCatalogEntry(
        "multi_tf.py",
        "multi_tf.MultiTf",
        PortStatus.PARTIAL,
        "Optional BTC/ETH informative pairs; core RSI stack ported.",
    ),
    "mabStra": StrategyCatalogEntry(
        "mabStra.py",
        "mab_stra.MabStra",
        PortStatus.PORTED,
        "Hyperopt defaults fixed; SMA ratio entry/exit.",
    ),
    "ReinforcedSmoothScalp": StrategyCatalogEntry(
        "berlinguyinca/ReinforcedSmoothScalp.py",
        "reinforced_smooth_scalp.ReinforcedSmoothScalp",
        PortStatus.PORTED,
        "5x trend SMA via trend_bar_type.",
    ),
    "FAdxSmaStrategy": StrategyCatalogEntry(
        "futures/FAdxSmaStrategy.py",
        "f_adx_sma.FAdxSma",
        PortStatus.PORTED,
        "Futures long/short ADX + SMA crossover.",
    ),
    "FOttStrategy": StrategyCatalogEntry(
        "futures/FOttStrategy.py",
        "f_ott.FOtt",
        PortStatus.PARTIAL,
        "OTT indicator streaming approximation; trailing stop not mapped.",
    ),
    "FReinforcedStrategy": StrategyCatalogEntry(
        "futures/FReinforcedStrategy.py",
        "f_reinforced.FReinforced",
        PortStatus.PORTED,
        "Futures EMA crossover with trend_bar_type SMA filter.",
    ),
    "FSampleStrategy": StrategyCatalogEntry(
        "futures/FSampleStrategy.py",
        "f_sample.FSample",
        PortStatus.PARTIAL,
        "HT_SINE indicators omitted (unused in signals).",
    ),
    "TrendFollowingStrategy": StrategyCatalogEntry(
        "futures/TrendFollowingStrategy.py",
        "trend_following.TrendFollowing",
        PortStatus.PORTED,
        "OBV + EMA trend long/short.",
    ),
    "VolatilitySystem": StrategyCatalogEntry(
        "futures/VolatilitySystem.py",
        "volatility_system.VolatilitySystem",
        PortStatus.PARTIAL,
        "3h ATR via resample_bar_type; position adjust/leverage omitted.",
    ),
    "Strategy001_custom_exit": StrategyCatalogEntry(
        "Strategy001_custom_exit.py",
        "strategy001_custom_exit.Strategy001CustomExit",
        PortStatus.PORTED,
        "custom_exit mapped to check_custom_exit on RSI + profit.",
    ),
    "GodStra": StrategyCatalogEntry(
        "GodStra.py",
        "god_stra.GodStra",
        PortStatus.PARTIAL,
        "Fixed genome only; ta add_all_ta_features not replicated.",
    ),
    "Heracles": StrategyCatalogEntry(
        "Heracles.py",
        "heracles.Heracles",
        PortStatus.PORTED,
        "Fixed buy genome; no sell signals in upstream.",
    ),
    "TDSequentialStrategy": StrategyCatalogEntry(
        "berlinguyinca/TDSequentialStrategy.py",
        "td_sequential.TdSequentialStrategy",
        PortStatus.PORTED,
        "TdSequential indicator; iterative exceed flags approximated.",
    ),
    "BinHV27": StrategyCatalogEntry(
        "berlinguyinca/BinHV27.py",
        "bin_hv27.BinHv27",
        PortStatus.PARTIAL,
        "Complex ADX/DI state machine; shift state approximated.",
    ),
    "BinHV45": StrategyCatalogEntry(
        "berlinguyinca/BinHV45.py",
        "bin_hv45.BinHv45",
        PortStatus.PORTED,
        "ROI-only exit in upstream; no exit signal here.",
    ),
    "CombinedBinHAndCluc": StrategyCatalogEntry(
        "berlinguyinca/CombinedBinHAndCluc.py",
        "combined_bin_h_cluc.CombinedBinHAndCluc",
        PortStatus.PORTED,
    ),
    "CofiBitStrategy": StrategyCatalogEntry(
        "berlinguyinca/CofiBitStrategy.py",
        "cofi_bit.CofiBit",
        PortStatus.PORTED,
    ),
    "EMASkipPump": StrategyCatalogEntry(
        "berlinguyinca/EMASkipPump.py",
        "ema_skip_pump.EmaSkipPump",
        PortStatus.PORTED,
        "Volume pump filter via rolling mean cap.",
    ),
    "SmoothOperator": StrategyCatalogEntry(
        "berlinguyinca/SmoothOperator.py",
        "smooth_operator.SmoothOperator",
        PortStatus.PARTIAL,
        "Active entry/exit branches only; commented upstream paths omitted.",
    ),
    "TrendRiderStrategy": StrategyCatalogEntry(
        "TrendRiderStrategy.py",
        "trend_rider.TrendRider",
        PortStatus.PARTIAL,
        "Primary-TF pullback/EMA subset; MTF/custom_exit/confirm omitted.",
    ),
    "ASDTSRockwellTrading": StrategyCatalogEntry(
        "berlinguyinca/ASDTSRockwellTrading.py",
        "asdts_rockwell.AsdtsRockwell",
        PortStatus.PORTED,
        "MACD above zero and signal line.",
    ),
    # --- Deprecated / educational ---
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
    "Freqtrade_backtest_validation_freqtrade1": StrategyCatalogEntry(
        "berlinguyinca/Freqtrade_backtest_validation_freqtrade1.py",
        None,
        PortStatus.DEPRECATED,
        "Validation harness, not a trading strategy.",
    ),
}


def catalog_summary() -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in FREQTRADE_STRATEGY_CATALOG.values():
        counts[entry.status] = counts.get(entry.status, 0) + 1
    return counts
