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
