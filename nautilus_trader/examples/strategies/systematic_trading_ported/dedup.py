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
Dedup mapping: awesome-systematic-trading alpha strategies → freqtrade_ported.

The awesome-systematic-trading repo is a curated link list; executable strategies
live in linked repos (primarily je-suis-tm/quant-trading).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DedupEntry:
    source_name: str
    source_repo: str
    duplicate_of: str | None
    nautilus_module: str | None
    reason: str


# je-suis-tm/quant-trading technical strategies (linked from awesome-systematic-trading)
QUANT_TRADING_DEDUP: dict[str, DedupEntry] = {
    "MACD Oscillator": DedupEntry(
        "MACD Oscillator backtest.py",
        "je-suis-tm/quant-trading",
        "freqtrade_ported.average_strategy.AverageStrategy",
        None,
        "SMA/EMA crossover when fast MA >= slow MA; same family as AverageStrategy.",
    ),
    "Awesome Oscillator": DedupEntry(
        "Awesome Oscillator backtest.py",
        "je-suis-tm/quant-trading",
        "freqtrade_ported.awesome_macd.AwesomeMacd",
        None,
        "AO momentum crossover + saucer; AwesomeMacd covers AO zero-cross + MACD filter.",
    ),
    "RSI Pattern Recognition": DedupEntry(
        "RSI Pattern Recognition backtest.py",
        "je-suis-tm/quant-trading",
        "freqtrade_ported.bband_rsi.BbandRsi",
        None,
        "RSI overbought/oversold mean reversion; equivalent to BbandRsi entry/exit thresholds.",
    ),
    "Heikin-Ashi (EMA combo)": DedupEntry(
        "Heikin-Ashi backtest.py vs Strategy001",
        "freqtrade vs quant-trading",
        "freqtrade_ported.strategy001.Strategy001",
        "systematic_trading_ported.heikin_ashi_marubozu.HeikinAshiMarubozu",
        "Strategy001 = HA + EMA crosses; quant-trading HA = marubozu body rules (ported separately).",
    ),
    "Dual Thrust": DedupEntry(
        "Dual Thrust backtest.py",
        "je-suis-tm/quant-trading",
        None,
        "systematic_trading_ported.dual_thrust.DualThrust",
        "Unique opening-range breakout; no freqtrade_ported equivalent.",
    ),
    "London Breakout": DedupEntry(
        "London Breakout backtest.py",
        "je-suis-tm/quant-trading",
        None,
        "systematic_trading_ported.london_breakout.LondonBreakout",
        "Unique session breakout; no freqtrade_ported equivalent.",
    ),
    "Parabolic SAR": DedupEntry(
        "Parabolic SAR backtest.py",
        "je-suis-tm/quant-trading",
        None,
        "systematic_trading_ported.parabolic_sar.ParabolicSarStrategy",
        "SAR trend follow; freqtrade blocked strategies use SAR but not ported.",
    ),
    "Bollinger Bands Pattern Recognition": DedupEntry(
        "Bollinger Bands Pattern Recognition backtest.py",
        "je-suis-tm/quant-trading",
        None,
        "systematic_trading_ported.bollinger_bottom_w.BollingerBottomW",
        "Bottom-W pattern; BbandRsi is RSI+BB mean reversion only.",
    ),
    "Shooting Star": DedupEntry(
        "Shooting Star backtest.py",
        "je-suis-tm/quant-trading",
        None,
        "systematic_trading_ported.shooting_star.ShootingStarExit",
        "Bearish pattern as long exit; distinct from freqtrade CDL strategies.",
    ),
    "Pair Trading": DedupEntry(
        "Pair trading backtest.py",
        "je-suis-tm/quant-trading",
        None,
        "systematic_trading_ported.pair_trading.PairTrading",
        "Two-instrument spread; no freqtrade_ported equivalent.",
    ),
    "Options Straddle": DedupEntry(
        "Options Straddle backtest.py",
        "je-suis-tm/quant-trading",
        None,
        None,
        "Options multi-leg; outside spot bar strategy scope.",
    ),
    "VIX Calculator": DedupEntry(
        "VIX Calculator.py",
        "je-suis-tm/quant-trading",
        None,
        None,
        "Vol index calculator, not a directional bar strategy.",
    ),
    "Monte Carlo Project": DedupEntry(
        "Monte Carlo project/",
        "je-suis-tm/quant-trading",
        None,
        None,
        "Quantamental simulation, not a trading signal strategy.",
    ),
    "Oil Money Project": DedupEntry(
        "Oil Money project/",
        "je-suis-tm/quant-trading",
        None,
        None,
        "Macro/commodity quantamental analysis.",
    ),
    "Smart Farmers Project": DedupEntry(
        "Smart Farmers project/",
        "je-suis-tm/quant-trading",
        None,
        None,
        "Agricultural demand forecasting, not bar-based TA.",
    ),
}
