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

"""Port of Freqtrade ``berlinguyinca/BinHV27``."""

from nautilus_trader.indicators import ExponentialMovingAverage
from nautilus_trader.indicators import RelativeStrengthIndex
from nautilus_trader.indicators import SimpleMovingAverage
from nautilus_trader.model.data import Bar

from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradeLongOnlyStrategy
from nautilus_trader.examples.strategies.freqtrade_ported.base import FreqtradePortConfig
from nautilus_trader.examples.strategies.freqtrade_ported.helpers import ShiftedValue
from nautilus_trader.examples.strategies.freqtrade_ported.indicators import AverageDirectionalIndex


class BinHv27Config(FreqtradePortConfig, frozen=True):
    """Configuration for ``BinHv27``."""


class BinHv27(FreqtradeLongOnlyStrategy):
    """Complex ADX/DI state machine (ported from BinHV27)."""

    def __init__(self, config: BinHv27Config) -> None:
        super().__init__(config)
        self._rsi = RelativeStrengthIndex(5)
        self._emarsi = ExponentialMovingAverage(5)
        self._adx = AverageDirectionalIndex(14)
        self._minusdi_ema = ExponentialMovingAverage(25)
        self._plusdi_ema = ExponentialMovingAverage(5)
        self._lowsma = ExponentialMovingAverage(60)
        self._highsma = ExponentialMovingAverage(120)
        self._fastsma = SimpleMovingAverage(120)
        self._slowsma = SimpleMovingAverage(240)
        self._prev_rsi = ShiftedValue()
        self._prev_trend = ShiftedValue()
        self._prev_trend2 = ShiftedValue()
        self._prev_slowsma = ShiftedValue()
        self._prev_slowsma2 = ShiftedValue()
        self._prev_fastsma = ShiftedValue()
        self._prev_delta = ShiftedValue()

    def _register_indicators(self) -> None:
        bar_type = self.port_config.bar_type
        for ind in (
            self._rsi,
            self._adx,
            self._lowsma,
            self._highsma,
            self._fastsma,
            self._slowsma,
        ):
            self.register_indicator_for_bars(bar_type, ind)

    def on_bar(self, bar: Bar) -> None:
        if bar.bar_type == self.port_config.bar_type:
            self._emarsi.update_raw(self._rsi.value * 100.0)
            self._minusdi_ema.update_raw(self._adx.minus_di)
            self._plusdi_ema.update_raw(self._adx.plus_di)
        super().on_bar(bar)

    def check_entry(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        prev_rsi = self._prev_rsi.update(self._rsi.value * 100.0)
        trend = self._fastsma.value - self._slowsma.value
        prev_trend = self._prev_trend.update(trend)
        prev_trend2 = self._prev_trend2.update(prev_trend) if prev_trend is not None else None
        prev_slow = self._prev_slowsma.update(self._slowsma.value)
        prev_slow2 = (
            self._prev_slowsma2.update(prev_slow) if prev_slow is not None else None
        )
        bigup = (
            self._fastsma.value > self._slowsma.value
            and (self._fastsma.value - self._slowsma.value) > close / 300.0
        )
        bigdown = not bigup
        prepare = prev_trend is not None and trend > prev_trend
        prepare_confirm = (
            prepare
            and prev_trend2 is not None
            and prev_trend > prev_trend2
        )
        continueup = (
            prev_slow is not None
            and prev_slow2 is not None
            and self._slowsma.value > prev_slow > prev_slow2
        )
        emarsi = self._emarsi.value
        base = (
            self._slowsma.value > 0
            and close < self._highsma.value
            and close < self._lowsma.value
            and self._adx.minus_di > self._minusdi_ema.value
            and prev_rsi is not None
            and self._rsi.value * 100.0 >= prev_rsi
        )
        path_a = (
            not prepare
            and not continueup
            and self._adx.adx > 25
            and bigdown
            and emarsi <= 20
        )
        path_b = (
            not prepare
            and continueup
            and self._adx.adx > 30
            and bigdown
            and emarsi <= 20
        )
        path_c = not continueup and self._adx.adx > 35 and bigup and emarsi <= 20
        path_d = continueup and self._adx.adx > 30 and bigup and emarsi <= 25
        return base and (path_a or path_b or path_c or path_d)

    def check_exit(self, bar: Bar) -> bool:
        close = bar.close.as_double()
        trend = self._fastsma.value - self._slowsma.value
        prev_trend = self._prev_trend.update(trend)
        prev_trend2 = self._prev_trend2.update(prev_trend) if prev_trend is not None else None
        prev_slow = self._prev_slowsma.update(self._slowsma.value)
        prev_slow2 = (
            self._prev_slowsma2.update(prev_slow) if prev_slow is not None else None
        )
        bigup = (
            self._fastsma.value > self._slowsma.value
            and (self._fastsma.value - self._slowsma.value) > close / 300.0
        )
        bigdown = not bigup
        prepare_confirm = (
            prev_trend is not None
            and prev_trend2 is not None
            and trend > prev_trend
            and prev_trend > prev_trend2
        )
        continueup = (
            prev_slow is not None
            and prev_slow2 is not None
            and self._slowsma.value > prev_slow > prev_slow2
        )
        emarsi = self._emarsi.value
        prev_fast = self._prev_fastsma.update(self._fastsma.value)
        fast_delta = self._fastsma.value - prev_fast if prev_fast is not None else 0.0
        prev_delta = self._prev_delta.update(fast_delta)
        slowing = prev_delta is not None and fast_delta < prev_delta
        return (
            (
                not prepare_confirm
                and not continueup
                and (close > self._lowsma.value or close > self._highsma.value)
                and self._highsma.value > 0
                and bigdown
            )
            or (
                not prepare_confirm
                and not continueup
                and close > self._highsma.value
                and self._highsma.value > 0
                and (emarsi >= 75 or close > self._slowsma.value)
                and bigdown
            )
            or (
                not prepare_confirm
                and close > self._highsma.value
                and self._highsma.value > 0
                and self._adx.adx > 30
                and emarsi >= 80
                and bigup
            )
            or (
                prepare_confirm
                and not continueup
                and slowing
                and emarsi >= 75
                and self._slowsma.value > 0
            )
            or (
                prepare_confirm
                and self._adx.minus_di < self._adx.plus_di
                and close > self._lowsma.value
                and self._slowsma.value > 0
            )
        )
