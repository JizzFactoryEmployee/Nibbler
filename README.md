# Nibbler

A library for crypto algorithmic trading

## Installation

To install requirements
````
python -m pip install -r requirements.txt
````
To install in symbolic mode,
````
python -m pip install -e .
````
To install in release mode,
````
python -m pip install .
````

## Data Collection
We provided a convenience wrapper over ccxt to simplify data collection. Data can be collected via collector classes found in the trading collectors module
````
nibbler.trading.collectors.{exchange}{asset}
````
For example collecting data from binance can be performed,
````
from nibbler import trading as td
from pathlib import Path
directory = Path(__file__).parent
filename = 'binance1h.csv'
filepath = directory/filename
collector = td.collectors.BinanceBTC('1h')
collector.run(filepath, multiplier=4)
````
Collectors run continuously until closed.

New collectors can be generated through inheritence of the Collector base class,
````
form nibbler.trading.collectors import Collector
class BinanceETH(Collector):
    _exchange = 'binance'
    symbol = 'ETH/USDT'
    limit = 1000

````
## Plotting Candlestick Data
Plotting of candlestick data is performed via bokeh.
````
from nibbler import plot
import pandas as pd

df = pd.read_csv({csv_file_path})
p = plot.candlesticks(df)
plot.show(p)
````
To plot directly from a csv file
````
p = plot.csv.candlesticks({csv_file_path})
plot.show(p)
````

## Indicators
The Indicator class wraps over functions which take in OHLCV information from a pandas dataframe. For example we can easily convert functions from the technical analysis https://technical-analysis-library-in-python.readthedocs.io/en/latest/ library into Indicators
````
import ta
from nibbler.trading import Indicators
# the rsi momentum indicator takes the form
# ta.momentum.rsi(close, n=14, fillna=False)
sma_indicator = Indicator(ta.trend.sma, n=21)
````
The Indicator class stores parameters of the function and integrate with time series forecast modules.

The Indicator class also contains convenience methods for visualization and random initialization.

````
import pandas as pd
from nibbler import plot
df = pd.read_csv({path_to_csv_file})
indicator_results = sma_indicator(df)
# we can plot the resulting indicator onto a figure of candlesticks with the
# the follwing methods
p = plot.candlesticks(df)
sma_indicator.plot(df, fig = p)
plot.show(p)
````
An indicator can be randomly initialized,
````
Indicator.random_initialization({function}, scale_default=3)
````
where ````scale_defaults```` scales the default arguments to set the maximum randmly initialized values. It is however reocmmended that the ````random_initialization```` be overridden for custom Indicators.

To generate static Indicators we can overide the ````__init__```` method of a child. For example let us generate a custom static indicator for savitzky golay filtering.

````
import savitzky_golay_open

class SavitzkyGolayBase(Indicator):
    @classmethod
    def random_initialization(cls, min_window, max_window, min_poly, max_poly):
        window_length = np.random.randint(min_window, max_window)
        poly = np.random.randint(
            min_poly, np.min([max_poly, window_length])
        )
        return cls( window_length=window_length, polyorder=poly,
        deriv=0, delta=1.0, mode='interp', cval=0)

class SavitzkyGolayOpen(SavitzkyGolayBase):

    def __init__(self, **kwargs):
        super().__init__(savitzky_golay_open, **kwargs)
````
## Signals
Signals take in a data frame then output either a true or false buy or sell signal. Signals are constructed from a set of features extracted from indicators. These features are the index location of the candlesticks of interest. The final signal and its features can be plotted with the ````plot_features```` and ````plot_signals```` methods of the Signal object. Buy features are denoted as green triangles, whilst  sell signals are in red inverted triangles. The buy signal itself is a yellow triangle whilst the sell signals are inverted yellow triangles

````
from nibbler import plot
from nibbler.trading.signals.buy import SavitzkyGolayMin
import pathlib as pt
import pandas as pd

cwd = pt.Path(__file__).parent

resources_folder = cwd/"../../resources"

corn_file = resources_folder/"BitcoinBinance1hr.csv"

signal = SavitzkyGolayMin()

df = pd.read_csv(corn_file)[-100:]

signallled = signal(df)

p = signal.plot_features(df)
p = signal.plot_signal(df, fig=p)

signal.clean()
````
The clean method is used when optimizing a signal. Signals can retain memory of prior signals to allow for easier plotting and to ensure that a signal, when lagging, is not repeated when using the same dataset.

Custom signals are inherited from either the BuySignal or SellSignal classes. As an examples the following shows a min finder signal,

````
from nibbler.trading.signals import BuySignal
from nibbler.trading.indicators.trend import SavitzkyGolayLow
from nibbler.trading.math import min_finder

import numpy as np

class SavitzkyGolayMin(BuySignal):

    # this method handles any removals necessary when changing datasets
    def clean(self):
        super().cleans()
        del self.past_signalled_features

    # this class method handles the random initialization
    @classmethod
    def random_initialization(cls, **kwargs):
        return cls(SavitzkyGolayLow.random_initialization(**kwargs))

    # The init method requires two methods for when
    # the Signal is initialized deterministically or randomly
    def __init__(self, *args, lag=20, **kwargs):
        if len(args) == 0:
            super().__init__(SavitzkyGolayLow(**kwargs))
        else:
            super().__init__(args)
        self.lag = lag
        self.past_signalled_features = []

    # the generate features method is used to create the
    # features necessary for the signal to operate
    def generate_features(self, dataframe):
        features = self.indicators[0](dataframe)
        features = min_finder(features)
        features = np.argwhere(features).squeeze()
        # features are of the form [1, 10, 2567, 8999,... etc]
        return features

    # the call method parses the output features and
    # returns either a true or false statement
    def __call__(self, dataframe):
        N = len(dataframe)
        features = self.generate_features(dataframe)
        latest_time_features = features[-1]
        if (latest_time_features + self.lag) > N:

            if latest_time_features \
                    in self.past_signalled_features:
                return False
            else:
                self.signalled.append(len(dataframe))
                self.past_signalled_features.append(latest_time_features)
                return True
````

In the above signal, as it is lagging, the past min features must be stored and checked to avoid repeating a signal. These types of checks must be taken into consideration when designing a strategy.

## Strategies and Optimiztion
A trading must take into consideration, to name a few, the following:
1. buy signal
2. stop
3. sell signal
4. entry method
5. target
6. exit method

### Strategies


### Brute Force Optimization