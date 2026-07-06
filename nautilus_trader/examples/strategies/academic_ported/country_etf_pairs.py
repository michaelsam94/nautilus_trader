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

"""Country ETF pair spread z-score mean reversion."""

from decimal import Decimal

from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.config import StrategyConfig
from nautilus_trader.model.data import BarType
from nautilus_trader.model.identifiers import InstrumentId

from nautilus_trader.examples.strategies.systematic_trading_ported.pair_trading import PairTrading
from nautilus_trader.examples.strategies.systematic_trading_ported.pair_trading import PairTradingConfig


class CountryEtfPairsConfig(StrategyConfig, frozen=True):
    """Configuration for ``CountryEtfPairs``."""

    instrument_id: InstrumentId
    hedge_instrument_id: InstrumentId
    bar_type: BarType
    hedge_bar_type: BarType
    trade_size: Decimal
    formation_period: PositiveInt = 120
    z_entry: PositiveFloat = 0.5
    request_historical_bars: bool = True
    historical_bars_days: PositiveInt = 200
    close_positions_on_stop: bool = True


class CountryEtfPairs(PairTrading):
    """
    Z-score mean reversion on a country-ETF pair.

    Simplified port of ``pairs-trading-with-country-etfs.py`` (pair
    selection and 20-day hold window omitted).
    """

    def __init__(self, config: CountryEtfPairsConfig) -> None:
        pair_config = PairTradingConfig(
            instrument_id=config.instrument_id,
            hedge_instrument_id=config.hedge_instrument_id,
            bar_type=config.bar_type,
            hedge_bar_type=config.hedge_bar_type,
            trade_size=config.trade_size,
            bandwidth=config.formation_period,
            z_entry=config.z_entry,
            request_historical_bars=config.request_historical_bars,
            historical_bars_days=config.historical_bars_days,
            close_positions_on_stop=config.close_positions_on_stop,
        )
        super().__init__(pair_config)
