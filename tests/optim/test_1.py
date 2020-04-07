import nibbler as nd
from nibbler.optim import BruteForceSingleDataset
from nibbler.trading.signals.buy.candlesticks import Doji
from nibbler.trading.signals.sell import SavitzkyGolayMaxFilteredGrads
from nibbler.trading.strategy import MarketLong
from nibbler.initialization import MarketStrategyInitialization
from nibbler import plot
import pandas as pd
import pathlib as pt

# setttings for the signals and the strategy
buy_signal_kwargs = dict(
    min_window=3, max_window=30,
    min_poly=3, max_poly=5
)

sell_signal_kwargs = dict(
    min_window=3, max_window=30,
    min_poly=3, max_poly=5
)

strategy_kwargs = dict(
    initial_account_balance = 1000,
    stop_calculator = None,
    slippage_frac = 0.0001,
    maker_fee_frac = 0.001,
    taker_fee_frac = 0.001,
    max_leverage = 100,
    use_leverage = False,
    leverage = 3
)

strategy_population = MarketStrategyInitialization(
    Doji,
    SavitzkyGolayMaxFilteredGrads,
    MarketLong,
    buy_signal_kwargs,
    sell_signal_kwargs,
    strategy_kwargs,
    n_population=50
)

# this guard is necessary for enabling multiprocesssing
if __name__ == "__main__":

    cwd = pt.Path(__file__).parent
    resource_folder = cwd/"../../resources"

    data_file = resource_folder/"BitcoinBinance1hr.csv"
    dataframe = pd.read_csv(data_file)

    optimizer = BruteForceSingleDataset(strategy_population)

    optimizer.calculate_fitness(dataframe.iloc[0:5000], n_processors=8)

    p = optimizer.population[-1].plot_trade_and_equity()

    plot.show(p)

    print(optimizer.population[-1].trade_log)

    nd.save(
        pt.Path(__file__).parent/"best_lad",
        optimizer.population[-1]
    )