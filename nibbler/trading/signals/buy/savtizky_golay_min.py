try:
    from nibbler.trading.signals import BuySignal
    from nibbler.trading.indicators.trend import SavitzkyGolayLow
    from nibbler.trading.math import min_finder
except:
    from .. import BuySignal
    from ...indicators.trend import SavitzkyGolayLow
    from nibbler.trading.math import min_finder

import numpy as np

class SavitzkyGolayMin(BuySignal):

    def clean(self):
        super().cleans()
        del self.past_signalled_features

    @classmethod
    def random_initialization(cls, **kwargs):
        return cls(SavitzkyGolayLow.random_initialization(**kwargs))

    def __init__(self, *args, lag=20, **kwargs):
        if len(args) == 0:
            super().__init__(SavitzkyGolayLow(**kwargs))
        else:
            super().__init__(args)
        self.lag = lag
        self.past_signalled_features = []

    def generate_features(self, dataframe):
        features = self.indicators[0](dataframe)
        features = min_finder(features)
        features = np.argwhere(features).squeeze()
        return features

    def __call__(self, dataframe):
        N = len(dataframe)
        features = self.generate_features(dataframe)
        latest_time_features = features[-1]
        if (latest_time_features + self.lag) > N:
            if latest_time_features in self.past_signalled_features:
                return False
            else:
                self.signalled.append(len(dataframe))
                self.past_signalled_features.append(latest_time_features)
                return True
