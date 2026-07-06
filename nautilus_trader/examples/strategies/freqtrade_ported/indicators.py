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
Python indicators used by ported Freqtrade strategies.

Built-in Nautilus indicators are preferred where available; this module fills
gaps for TALib/qtpylib helpers commonly used in the Freqtrade strategy repo.
"""

from __future__ import annotations

from collections import deque

from nautilus_trader.core.correctness import PyCondition
from nautilus_trader.indicators import ExponentialMovingAverage
from nautilus_trader.indicators import Indicator
from nautilus_trader.indicators import MovingAverageConvergenceDivergence
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar


class MacdWithSignal(Indicator):
    """
    MACD line with signal line and histogram (TALib-compatible layout).

    Parameters
    ----------
    fast_period : int
        Fast EMA period (default 12).
    slow_period : int
        Slow EMA period (default 26).
    signal_period : int
        Signal EMA period (default 9).
    """

    def __init__(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> None:
        PyCondition.positive_int(fast_period, "fast_period")
        PyCondition.positive_int(slow_period, "slow_period")
        PyCondition.positive_int(signal_period, "signal_period")
        super().__init__(params=[fast_period, slow_period, signal_period])

        self._macd = MovingAverageConvergenceDivergence(fast_period, slow_period)
        self._signal = ExponentialMovingAverage(signal_period)
        self.macd: float = 0.0
        self.signal: float = 0.0
        self.histogram: float = 0.0

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        self._macd.handle_bar(bar)
        if not self._macd.initialized:
            return

        self.macd = self._macd.value
        self._signal.update_raw(self.macd)
        self.signal = self._signal.value
        self.histogram = self.macd - self.signal

        if not self.initialized:
            self._set_has_inputs(True)
            if self._signal.initialized:
                self._set_initialized(True)

    def _reset(self) -> None:
        self._macd.reset()
        self._signal.reset()
        self.macd = 0.0
        self.signal = 0.0
        self.histogram = 0.0


class AverageDirectionalIndex(Indicator):
    """
    ADX, +DI, and -DI using Wilder smoothing (TALib-compatible periods).
    """

    def __init__(self, period: int = 14) -> None:
        PyCondition.positive_int(period, "period")
        super().__init__(params=[period])
        self.period = period
        self.adx: float = 0.0
        self.plus_di: float = 0.0
        self.minus_di: float = 0.0

        self._prev_high: float | None = None
        self._prev_low: float | None = None
        self._prev_close: float | None = None
        self._tr_sum: float = 0.0
        self._plus_dm_sum: float = 0.0
        self._minus_dm_sum: float = 0.0
        self._dx_values: deque[float] = deque(maxlen=period)
        self._count = 0

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        high = bar.high.as_double()
        low = bar.low.as_double()
        close = bar.close.as_double()

        if self._prev_high is None:
            self._prev_high = high
            self._prev_low = low
            self._prev_close = close
            self._set_has_inputs(True)
            return

        up_move = high - self._prev_high
        down_move = self._prev_low - low
        plus_dm = up_move if up_move > down_move and up_move > 0 else 0.0
        minus_dm = down_move if down_move > up_move and down_move > 0 else 0.0
        tr = max(high - low, abs(high - self._prev_close), abs(low - self._prev_close))

        self._count += 1
        if self._count <= self.period:
            self._tr_sum += tr
            self._plus_dm_sum += plus_dm
            self._minus_dm_sum += minus_dm
        else:
            self._tr_sum = self._tr_sum - (self._tr_sum / self.period) + tr
            self._plus_dm_sum = self._plus_dm_sum - (self._plus_dm_sum / self.period) + plus_dm
            self._minus_dm_sum = self._minus_dm_sum - (self._minus_dm_sum / self.period) + minus_dm

        if self._count >= self.period and self._tr_sum > 0:
            self.plus_di = 100.0 * self._plus_dm_sum / self._tr_sum
            self.minus_di = 100.0 * self._minus_dm_sum / self._tr_sum
            di_sum = self.plus_di + self.minus_di
            dx = abs(self.plus_di - self.minus_di) / di_sum * 100.0 if di_sum > 0 else 0.0
            self._dx_values.append(dx)
            if len(self._dx_values) == self.period:
                self.adx = sum(self._dx_values) / self.period
                self._set_initialized(True)

        self._prev_high = high
        self._prev_low = low
        self._prev_close = close

    def _reset(self) -> None:
        self.adx = 0.0
        self.plus_di = 0.0
        self.minus_di = 0.0
        self._prev_high = None
        self._prev_low = None
        self._prev_close = None
        self._tr_sum = 0.0
        self._plus_dm_sum = 0.0
        self._minus_dm_sum = 0.0
        self._dx_values.clear()
        self._count = 0


class HeikinAshi(Indicator):
    """Heikin Ashi OHLC transform."""

    def __init__(self) -> None:
        super().__init__(params=[])
        self.open: float = 0.0
        self.high: float = 0.0
        self.low: float = 0.0
        self.close: float = 0.0
        self._prev_ha_open: float | None = None
        self._prev_ha_close: float | None = None

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        o = bar.open.as_double()
        h = bar.high.as_double()
        l = bar.low.as_double()
        c = bar.close.as_double()

        ha_close = (o + h + l + c) / 4.0
        if self._prev_ha_open is None:
            ha_open = (o + c) / 2.0
        else:
            ha_open = (self._prev_ha_open + self._prev_ha_close) / 2.0

        ha_high = max(h, ha_open, ha_close)
        ha_low = min(l, ha_open, ha_close)

        self.open = ha_open
        self.high = ha_high
        self.low = ha_low
        self.close = ha_close

        self._prev_ha_open = ha_open
        self._prev_ha_close = ha_close

        if not self.has_inputs:
            self._set_has_inputs(True)
        if not self.initialized:
            self._set_initialized(True)

    def is_green(self) -> bool:
        return self.open < self.close

    def is_red(self) -> bool:
        return self.open > self.close

    def _reset(self) -> None:
        self.open = 0.0
        self.high = 0.0
        self.low = 0.0
        self.close = 0.0
        self._prev_ha_open = None
        self._prev_ha_close = None


class AwesomeOscillator(Indicator):
    """Awesome Oscillator: SMA5(median) - SMA34(median)."""

    def __init__(self, fast_period: int = 5, slow_period: int = 34) -> None:
        PyCondition.positive_int(fast_period, "fast_period")
        PyCondition.positive_int(slow_period, "slow_period")
        super().__init__(params=[fast_period, slow_period])
        self._fast = SimpleMovingAverage(fast_period)
        self._slow = SimpleMovingAverage(slow_period)
        self.value: float = 0.0
        self._prev_value: float | None = None

    @property
    def previous(self) -> float | None:
        return self._prev_value

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        median = (bar.high.as_double() + bar.low.as_double()) / 2.0
        self._fast.update_raw(median)
        self._slow.update_raw(median)
        if self._fast.initialized and self._slow.initialized:
            self._prev_value = self.value
            self.value = self._fast.value - self._slow.value
            if not self.initialized:
                self._set_has_inputs(True)
                self._set_initialized(True)

    def crossed_above_zero(self) -> bool:
        if self._prev_value is None:
            return False
        return self._prev_value < 0.0 and self.value > 0.0

    def crossed_below_zero(self) -> bool:
        if self._prev_value is None:
            return False
        return self._prev_value > 0.0 and self.value < 0.0

    def _reset(self) -> None:
        self._fast.reset()
        self._slow.reset()
        self.value = 0.0
        self._prev_value = None


class MoneyFlowIndex(Indicator):
    """Money Flow Index (0-100 scale, TALib-compatible)."""

    def __init__(self, period: int = 14) -> None:
        PyCondition.positive_int(period, "period")
        super().__init__(params=[period])
        self.period = period
        self.value: float = 0.0
        self._prev_typical: float | None = None
        self._positive_flow: deque[float] = deque(maxlen=period)
        self._negative_flow: deque[float] = deque(maxlen=period)

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        typical = (
            bar.high.as_double() + bar.low.as_double() + bar.close.as_double()
        ) / 3.0
        raw_volume = float(bar.volume) if bar.volume is not None else 0.0

        if self._prev_typical is not None:
            raw_money = typical * raw_volume
            if typical > self._prev_typical:
                self._positive_flow.append(raw_money)
                self._negative_flow.append(0.0)
            elif typical < self._prev_typical:
                self._positive_flow.append(0.0)
                self._negative_flow.append(raw_money)
            else:
                self._positive_flow.append(0.0)
                self._negative_flow.append(0.0)

            if len(self._positive_flow) >= self.period:
                pos = sum(self._positive_flow)
                neg = sum(self._negative_flow)
                if neg == 0:
                    self.value = 100.0
                else:
                    ratio = pos / neg
                    self.value = 100.0 - (100.0 / (1.0 + ratio))
                if not self.initialized:
                    self._set_has_inputs(True)
                    self._set_initialized(True)

        self._prev_typical = typical

    def _reset(self) -> None:
        self.value = 0.0
        self._prev_typical = None
        self._positive_flow.clear()
        self._negative_flow.clear()


class ChandeMomentumOscillator(Indicator):
    """Chande Momentum Oscillator (-100 to +100)."""

    def __init__(self, period: int = 14) -> None:
        PyCondition.positive_int(period, "period")
        super().__init__(params=[period])
        self.period = period
        self.value: float = 0.0
        self._prev_close: float | None = None
        self._gains: deque[float] = deque(maxlen=period)
        self._losses: deque[float] = deque(maxlen=period)

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        close = bar.close.as_double()
        if self._prev_close is not None:
            diff = close - self._prev_close
            self._gains.append(max(diff, 0.0))
            self._losses.append(max(-diff, 0.0))
            if len(self._gains) >= self.period:
                sum_gain = sum(self._gains)
                sum_loss = sum(self._losses)
                total = sum_gain + sum_loss
                self.value = 100.0 * (sum_gain - sum_loss) / total if total > 0 else 0.0
                if not self.initialized:
                    self._set_has_inputs(True)
                    self._set_initialized(True)
        self._prev_close = close

    def _reset(self) -> None:
        self.value = 0.0
        self._prev_close = None
        self._gains.clear()
        self._losses.clear()


class ChaikinMoneyFlow(Indicator):
    """Chaikin Money Flow oscillator."""

    def __init__(self, period: int = 20) -> None:
        PyCondition.positive_int(period, "period")
        super().__init__(params=[period])
        self.period = period
        self.value: float = 0.0
        self._mfv_window: deque[float] = deque(maxlen=period)
        self._volume_window: deque[float] = deque(maxlen=period)

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        high = bar.high.as_double()
        low = bar.low.as_double()
        close = bar.close.as_double()
        volume = float(bar.volume) if bar.volume is not None else 0.0

        if high == low:
            mfv = 0.0
        else:
            mfv = ((close - low) - (high - close)) / (high - low) * volume

        self._mfv_window.append(mfv)
        self._volume_window.append(volume)

        if len(self._mfv_window) >= self.period:
            vol_sum = sum(self._volume_window)
            self.value = sum(self._mfv_window) / vol_sum if vol_sum > 0 else 0.0
            if not self.initialized:
                self._set_has_inputs(True)
                self._set_initialized(True)

    def _reset(self) -> None:
        self.value = 0.0
        self._mfv_window.clear()
        self._volume_window.clear()


class ExponentialMovingAverageOnHigh(Indicator):
    """EMA computed on bar high prices."""

    def __init__(self, period: int) -> None:
        PyCondition.positive_int(period, "period")
        super().__init__(params=[period])
        self._ema = ExponentialMovingAverage(period)
        self.value: float = 0.0

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        self._ema.update_raw(bar.high.as_double())
        self.value = self._ema.value
        if not self.initialized:
            self._set_has_inputs(True)
            if self._ema.initialized:
                self._set_initialized(True)

    def _reset(self) -> None:
        self._ema.reset()
        self.value = 0.0


class TripleExponentialMovingAverage(Indicator):
    """TEMA: triple-smoothed EMA (TALib-compatible)."""

    def __init__(self, period: int) -> None:
        PyCondition.positive_int(period, "period")
        super().__init__(params=[period])
        self._ema1 = ExponentialMovingAverage(period)
        self._ema2 = ExponentialMovingAverage(period)
        self._ema3 = ExponentialMovingAverage(period)
        self.value: float = 0.0

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        close = bar.close.as_double()
        self._ema1.update_raw(close)
        if not self._ema1.initialized:
            return
        self._ema2.update_raw(self._ema1.value)
        if not self._ema2.initialized:
            return
        self._ema3.update_raw(self._ema2.value)
        if not self._ema3.initialized:
            return
        self.value = 3.0 * self._ema1.value - 3.0 * self._ema2.value + self._ema3.value
        if not self.initialized:
            self._set_has_inputs(True)
            self._set_initialized(True)

    def _reset(self) -> None:
        self._ema1.reset()
        self._ema2.reset()
        self._ema3.reset()
        self.value = 0.0


class SuperTrend(Indicator):
    """
    SuperTrend line with direction (+1 uptrend, -1 downtrend).

    Uses Wilder ATR bands with standard final-band ratcheting.
    """

    def __init__(self, period: int = 10, multiplier: float = 3.0) -> None:
        PyCondition.positive_int(period, "period")
        PyCondition.is_true(multiplier > 0, "multiplier must be positive")
        super().__init__(params=[period, multiplier])
        from nautilus_trader.indicators import AverageTrueRange

        self._atr = AverageTrueRange(period)
        self.period = period
        self.multiplier = multiplier
        self.line: float = 0.0
        self.direction: int = 1
        self._final_upper: float = 0.0
        self._final_lower: float = 0.0
        self._prev_close: float | None = None

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        high = bar.high.as_double()
        low = bar.low.as_double()
        close = bar.close.as_double()
        self._atr.handle_bar(bar)
        if not self._atr.initialized:
            return

        hl2 = (high + low) / 2.0
        atr = self._atr.value
        basic_upper = hl2 + self.multiplier * atr
        basic_lower = hl2 - self.multiplier * atr

        if self._prev_close is None:
            self._final_upper = basic_upper
            self._final_lower = basic_lower
            self.line = basic_upper
            self.direction = 1
            self._prev_close = close
            self._set_has_inputs(True)
            return

        if basic_upper < self._final_upper or self._prev_close > self._final_upper:
            self._final_upper = basic_upper
        if basic_lower > self._final_lower or self._prev_close < self._final_lower:
            self._final_lower = basic_lower

        if self.line == self._final_upper:
            if close > self._final_upper:
                self.line = self._final_lower
                self.direction = 1
            else:
                self.line = self._final_upper
                self.direction = -1
        elif close < self._final_lower:
            self.line = self._final_upper
            self.direction = -1
        else:
            self.line = self._final_lower
            self.direction = 1

        self._prev_close = close
        if not self.initialized:
            self._set_initialized(True)

    def is_up(self) -> bool:
        """Freqtrade ``STX == 'up'`` equivalent."""
        return self.direction == 1

    def is_down(self) -> bool:
        """Freqtrade ``STX == 'down'`` equivalent."""
        return self.direction == -1

    def _reset(self) -> None:
        self._atr.reset()
        self.line = 0.0
        self.direction = 1
        self._final_upper = 0.0
        self._final_lower = 0.0
        self._prev_close = None


class UniversalMacdRatio(Indicator):
    """Universal MACD: (EMA12 / EMA26) - 1."""

    def __init__(self, fast_period: int = 12, slow_period: int = 26) -> None:
        PyCondition.positive_int(fast_period, "fast_period")
        PyCondition.positive_int(slow_period, "slow_period")
        super().__init__(params=[fast_period, slow_period])
        self._fast = ExponentialMovingAverage(fast_period)
        self._slow = ExponentialMovingAverage(slow_period)
        self.value: float = 0.0

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        close = bar.close.as_double()
        self._fast.update_raw(close)
        self._slow.update_raw(close)
        if self._fast.initialized and self._slow.initialized and self._slow.value != 0:
            self.value = (self._fast.value / self._slow.value) - 1.0
            if not self.initialized:
                self._set_has_inputs(True)
                self._set_initialized(True)

    def _reset(self) -> None:
        self._fast.reset()
        self._slow.reset()
        self.value = 0.0


class ExponentialMovingAverageOnLow(Indicator):
    """EMA computed on bar low prices."""

    def __init__(self, period: int) -> None:
        PyCondition.positive_int(period, "period")
        super().__init__(params=[period])
        self._ema = ExponentialMovingAverage(period)
        self.value: float = 0.0

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        self._ema.update_raw(bar.low.as_double())
        self.value = self._ema.value
        if not self.initialized:
            self._set_has_inputs(True)
            if self._ema.initialized:
                self._set_initialized(True)

    def _reset(self) -> None:
        self._ema.reset()
        self.value = 0.0


class ExponentialMovingAverageOnClose(Indicator):
    """EMA computed on bar close prices."""

    def __init__(self, period: int) -> None:
        PyCondition.positive_int(period, "period")
        super().__init__(params=[period])
        self._ema = ExponentialMovingAverage(period)
        self.value: float = 0.0

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        self._ema.update_raw(bar.close.as_double())
        self.value = self._ema.value
        if not self.initialized:
            self._set_has_inputs(True)
            if self._ema.initialized:
                self._set_initialized(True)

    def _reset(self) -> None:
        self._ema.reset()
        self.value = 0.0


class BollingerBandsOnTypicalPrice(Indicator):
    """Bollinger bands on typical price (H+L+C)/3."""

    def __init__(self, period: int = 20, std_dev: float = 2.0) -> None:
        PyCondition.positive_int(period, "period")
        PyCondition.is_true(std_dev > 0, "std_dev must be positive")
        super().__init__(params=[period, std_dev])
        from nautilus_trader.indicators import BollingerBands

        self._bb = BollingerBands(period, std_dev)
        self.period = period
        self.std_dev = std_dev
        self.upper: float = 0.0
        self.middle: float = 0.0
        self.lower: float = 0.0

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        typical = (
            bar.high.as_double() + bar.low.as_double() + bar.close.as_double()
        ) / 3.0
        self._bb.update_raw(typical)
        self.upper = self._bb.upper
        self.middle = self._bb.middle
        self.lower = self._bb.lower
        if not self.initialized:
            self._set_has_inputs(True)
            if self._bb.initialized:
                self._set_initialized(True)

    def _reset(self) -> None:
        self._bb.reset()
        self.upper = 0.0
        self.middle = 0.0
        self.lower = 0.0


class RollingMinimum(Indicator):
    """Rolling minimum of close prices."""

    def __init__(self, period: int) -> None:
        PyCondition.positive_int(period, "period")
        super().__init__(params=[period])
        self.period = period
        self.value: float = 0.0
        self._window: deque[float] = deque(maxlen=period)

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        self._window.append(bar.close.as_double())
        self.value = min(self._window)
        if not self.initialized and len(self._window) >= self.period:
            self._set_has_inputs(True)
            self._set_initialized(True)

    def _reset(self) -> None:
        self._window.clear()
        self.value = 0.0


class RollingMaximum(Indicator):
    """Rolling maximum of close prices."""

    def __init__(self, period: int) -> None:
        PyCondition.positive_int(period, "period")
        super().__init__(params=[period])
        self.period = period
        self.value: float = 0.0
        self._window: deque[float] = deque(maxlen=period)

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        self._window.append(bar.close.as_double())
        self.value = max(self._window)
        if not self.initialized and len(self._window) >= self.period:
            self._set_has_inputs(True)
            self._set_initialized(True)

    def _reset(self) -> None:
        self._window.clear()
        self.value = 0.0


class ParabolicSAR(Indicator):
    """Parabolic SAR (TALib-compatible defaults: af=0.02, max_af=0.2)."""

    def __init__(self, af_start: float = 0.02, af_max: float = 0.2) -> None:
        PyCondition.is_true(0 < af_start <= af_max, "invalid acceleration factor bounds")
        super().__init__(params=[af_start, af_max])
        self.af_start = af_start
        self.af_max = af_max
        self.value: float = 0.0
        self._prev_high: float | None = None
        self._prev_low: float | None = None
        self._prev_sar: float | None = None
        self._ep: float | None = None
        self._af: float = af_start
        self._rising: bool = True

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        high = bar.high.as_double()
        low = bar.low.as_double()

        if self._prev_high is None:
            self._prev_high = high
            self._prev_low = low
            self._prev_sar = low
            self._ep = high
            self.value = low
            self._set_has_inputs(True)
            return

        sar = self._prev_sar
        if self._rising:
            sar = min(sar, self._prev_low, low)
            if high > self._ep:
                self._ep = high
                self._af = min(self._af + self.af_start, self.af_max)
            if low < sar:
                self._rising = False
                sar = self._ep
                self._ep = low
                self._af = self.af_start
        else:
            sar = max(sar, self._prev_high, high)
            if low < self._ep:
                self._ep = low
                self._af = min(self._af + self.af_start, self.af_max)
            if high > sar:
                self._rising = True
                sar = self._ep
                self._ep = high
                self._af = self.af_start

        self.value = sar
        self._prev_sar = sar
        self._prev_high = high
        self._prev_low = low
        if not self.initialized:
            self._set_initialized(True)

    def _reset(self) -> None:
        self.value = 0.0
        self._prev_high = None
        self._prev_low = None
        self._prev_sar = None
        self._ep = None
        self._af = self.af_start
        self._rising = True


class HammerPattern(Indicator):
    """
    Hammer candlestick detector.

    Returns 100 when hammer detected, 0 otherwise (TALib CDLHAMMER scale).
    """

    def __init__(self) -> None:
        super().__init__(params=[])
        self.value: float = 0.0

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        o = bar.open.as_double()
        h = bar.high.as_double()
        l = bar.low.as_double()
        c = bar.close.as_double()
        body = abs(c - o)
        lower_shadow = min(o, c) - l
        upper_shadow = h - max(o, c)
        if body == 0:
            body = 1e-12
        self.value = (
            100.0
            if lower_shadow >= 2.0 * body and upper_shadow <= body
            else 0.0
        )
        if not self.has_inputs:
            self._set_has_inputs(True)
        if not self.initialized:
            self._set_initialized(True)

    def _reset(self) -> None:
        self.value = 0.0


class HighWavePattern(Indicator):
    """
    High-wave candlestick detector (TALib CDLHIGHWAVE approximation).

    Returns -100 when detected, 0 otherwise.
    """

    def __init__(self) -> None:
        super().__init__(params=[])
        self.value: float = 0.0

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        o = bar.open.as_double()
        h = bar.high.as_double()
        l = bar.low.as_double()
        c = bar.close.as_double()
        body = abs(c - o)
        upper = h - max(o, c)
        lower = min(o, c) - l
        if body == 0:
            body = 1e-12
        self.value = (
            -100.0
            if upper >= 3.0 * body and lower >= 3.0 * body
            else 0.0
        )
        if not self.has_inputs:
            self._set_has_inputs(True)
        if not self.initialized:
            self._set_initialized(True)

    def _reset(self) -> None:
        self.value = 0.0


class KeltnerChannelWidth(Indicator):
    """Keltner channel width band (ta.volatility.keltner_channel_wband approximation)."""

    def __init__(self, window: int = 20, atr_window: int = 10) -> None:
        PyCondition.positive_int(window, "window")
        PyCondition.positive_int(atr_window, "atr_window")
        super().__init__(params=[window, atr_window])
        from nautilus_trader.indicators import AverageTrueRange
        from nautilus_trader.indicators import ExponentialMovingAverage

        self._ema = ExponentialMovingAverage(window)
        self._atr = AverageTrueRange(atr_window)
        self.value: float = 0.0

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        self._ema.handle_bar(bar)
        self._atr.handle_bar(bar)
        if self._ema.initialized and self._atr.initialized and self._ema.value != 0:
            upper = self._ema.value + 2.0 * self._atr.value
            lower = self._ema.value - 2.0 * self._atr.value
            self.value = (upper - lower) / self._ema.value
            if not self.initialized:
                self._set_has_inputs(True)
                self._set_initialized(True)

    def _reset(self) -> None:
        self._ema.reset()
        self._atr.reset()
        self.value = 0.0


class DonchianChannelPercent(Indicator):
    """Donchian channel percent band (ta.volatility.donchian_channel_pband approximation)."""

    def __init__(self, window: int = 10) -> None:
        PyCondition.positive_int(window, "window")
        super().__init__(params=[window])
        self.window = window
        self.value: float = 0.0
        self._highs: deque[float] = deque(maxlen=window)
        self._lows: deque[float] = deque(maxlen=window)

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        self._highs.append(bar.high.as_double())
        self._lows.append(bar.low.as_double())
        if len(self._highs) >= self.window:
            highest = max(self._highs)
            lowest = min(self._lows)
            span = highest - lowest
            close = bar.close.as_double()
            self.value = (close - lowest) / span if span > 0 else 0.5
            if not self.initialized:
                self._set_has_inputs(True)
                self._set_initialized(True)

    def _reset(self) -> None:
        self._highs.clear()
        self._lows.clear()
        self.value = 0.0


class OttIndicator(Indicator):
    """
    Optimized Trend Tracker (OTT) from Freqtrade FOttStrategy.

    Exposes ``var`` and ``ott`` lines; ``ott`` is lagged two bars like upstream.
    """

    def __init__(self, pds: int = 2, percent: float = 1.4) -> None:
        super().__init__(params=[pds, percent])
        self.pds = pds
        self.percent = percent
        self.alpha = 2.0 / (pds + 1)
        self.var: float = 0.0
        self.ott: float = 0.0
        self._ud1_window: deque[float] = deque(maxlen=9)
        self._dd1_window: deque[float] = deque(maxlen=9)
        self._prev_close: float | None = None
        self._longstop: float = 0.0
        self._shortstop: float = 1e18
        self._dir: int = 1
        self._ott_history: deque[float] = deque(maxlen=3)

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        close = bar.close.as_double()
        if self._prev_close is None:
            self._prev_close = close
            self.var = close
            self._set_has_inputs(True)
            return

        ud1 = max(close - self._prev_close, 0.0) if close > self._prev_close else 0.0
        dd1 = max(self._prev_close - close, 0.0) if close < self._prev_close else 0.0
        self._ud1_window.append(ud1)
        self._dd1_window.append(dd1)
        ud = sum(self._ud1_window)
        dd = sum(self._dd1_window)
        cmo = abs((ud - dd) / (ud + dd)) if (ud + dd) > 0 else 0.0

        prev_var = self.var
        self.var = self.alpha * cmo * close + (1.0 - self.alpha * cmo) * self.var
        fark = self.var * self.percent * 0.01
        new_longstop = self.var - fark
        new_shortstop = self.var + fark

        if self.var > self._longstop:
            self._longstop = max(new_longstop, self._longstop)
        else:
            self._longstop = new_longstop

        if self.var < self._shortstop:
            self._shortstop = min(new_shortstop, self._shortstop)
        else:
            self._shortstop = new_shortstop

        xlong = self.var < self._longstop and prev_var > self._longstop
        xshort = self.var > self._shortstop and prev_var < self._shortstop
        if xshort:
            self._dir = 1
        elif xlong:
            self._dir = -1

        mt = self._longstop if self._dir == 1 else self._shortstop
        raw_ott = (
            mt * (200.0 + self.percent) / 200.0
            if self.var > mt
            else mt * (200.0 - self.percent) / 200.0
        )
        self._ott_history.append(raw_ott)
        self.ott = self._ott_history[0] if len(self._ott_history) >= 3 else raw_ott
        self._prev_close = close
        if not self.initialized and len(self._ud1_window) >= 9:
            self._set_initialized(True)

    def _reset(self) -> None:
        self.var = 0.0
        self.ott = 0.0
        self._ud1_window.clear()
        self._dd1_window.clear()
        self._prev_close = None
        self._longstop = 0.0
        self._shortstop = 1e18
        self._dir = 1
        self._ott_history.clear()


class TdSequential(Indicator):
    """
    TD Sequential buy/sell setup counter (simplified from TDSequentialStrategy).

    ``exceed_low`` / ``exceed_high`` flags ideal entry/exit bar conditions.
    """

    def __init__(self) -> None:
        super().__init__(params=[])
        self.buy_setup: int = 0
        self.sell_setup: int = 0
        self.exceed_low: bool = False
        self.exceed_high: bool = False
        self._closes: deque[float] = deque(maxlen=20)
        self._lows: deque[float] = deque(maxlen=20)
        self._highs: deque[float] = deque(maxlen=20)
        self._prev_exceed_low: bool = False

    def handle_bar(self, bar: Bar) -> None:
        PyCondition.not_none(bar, "bar")
        close = bar.close.as_double()
        low = bar.low.as_double()
        high = bar.high.as_double()
        self._closes.append(close)
        self._lows.append(low)
        self._highs.append(high)

        if len(self._closes) > 4:
            ref = self._closes[-5]
            if close < ref:
                self.buy_setup = self.buy_setup + 1 if self.buy_setup > 0 else 1
                self.sell_setup = 0
            elif close > ref:
                self.sell_setup = self.sell_setup + 1 if self.sell_setup > 0 else 1
                self.buy_setup = 0
            else:
                self.buy_setup = 0
                self.sell_setup = 0
        else:
            self.buy_setup = 0
            self.sell_setup = 0

        self.exceed_low = False
        self.exceed_high = False
        seq_b = self.buy_setup
        seq_s = self.sell_setup
        if seq_b >= 8 and len(self._lows) >= 3:
            if seq_b == 8:
                self.exceed_low = low < self._lows[-3] or low < self._lows[-2]
            elif seq_b > 8:
                off = seq_b - 9
                i0 = -(4 + off)
                i1 = -(3 + off)
                if abs(i0) <= len(self._lows) and abs(i1) <= len(self._lows):
                    self.exceed_low = low < self._lows[i0] or low < self._lows[i1]
                if seq_b == 9:
                    self.exceed_low = self.exceed_low or self._prev_exceed_low
        if seq_s >= 8 and len(self._highs) >= 3:
            if seq_s == 8:
                self.exceed_high = high > self._highs[-3] or high > self._highs[-2]
            elif seq_s > 8:
                off = seq_s - 9
                i0 = -(4 + off)
                i1 = -(3 + off)
                if abs(i0) <= len(self._highs) and abs(i1) <= len(self._highs):
                    self.exceed_high = high > self._highs[i0] or high > self._highs[i1]

        self._prev_exceed_low = self.exceed_low
        if not self.has_inputs:
            self._set_has_inputs(True)
        if not self.initialized and len(self._closes) >= 10:
            self._set_initialized(True)

    def _reset(self) -> None:
        self.buy_setup = 0
        self.sell_setup = 0
        self.exceed_low = False
        self.exceed_high = False
        self._closes.clear()
        self._lows.clear()
        self._highs.clear()
        self._prev_exceed_low = False
