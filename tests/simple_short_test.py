import unittest
import pandas as pd 
import numpy as np
import sys

sys.path.insert(1, "src")

from FastTest import FastTest
from Exchange import Exchange
from Broker import Broker
from Strategy import Strategy, BenchMarkBH
from Asset import Asset
from Order import *

class TestSimpleShort(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

        self.exchange = Exchange()
        self.broker = Broker(exchange=self.exchange)
        

        source_type = "csv"
        datetime_format = "%Y-%m-%d"
        datetime_column = "DATE"

        for asset_name in ["test1","test2"]:
            self.exchange.register_asset(Asset(
                        asset_name,
                        source_type = source_type,
                        csv_path = r"tests\data\{}.csv".format(asset_name),
                        datetime_format = datetime_format,
                        datetime_column = datetime_column,
                        frequency = "1D"
                    )
                )
        self.fast_test = FastTest(
            exchange=self.exchange,
            broker=self.broker
        )

    def test_market_order_short(self):
        """
        Test:
        sell 100 shares of test1 at first available open and hold till last close
        """
        self.exchange.reset()
        self.broker.reset()
        
        class BasicStrategy(Strategy):
            def __init__(self, exchange: Exchange, broker: Broker) -> None:
                super().__init__(exchange, broker)

            def next(self):
                current_time = self.exchange.market_time
                if str(current_time.date()) == "2000-06-06":
                    new_order = MarketOrder(
                        order_create_time = self.exchange.market_time,
                        asset_name = "test1",
                        units = -100
                    )
                    return [new_order]
                else:
                    return []

        strategy = BasicStrategy(
            exchange=self.exchange,
            broker=self.broker
        )
        self.fast_test.register_strategy(strategy)
        self.fast_test.run()  

        strategy_analysis = self.broker.strategy_analysis
        position_history = self.broker.position_history
        portfolio_value_history = self.fast_test.portfolio_history["net_liquidation_value"].values.tolist()

        assert(position_history[0].realized_pl == -400)
        assert(position_history[0].unrealized_pl == 0)
        assert(position_history[0].units == -100)
        assert(portfolio_value_history == [100000,100000,99900,99700,99600,99600])
        assert(self.fast_test.portfolio_history["cash"].values.tolist() == [100000,100000,99900,99700,99600,99600])
        assert(self.fast_test.position_history_df["realized_pl"].sum() == portfolio_value_history[-1] - portfolio_value_history[0])

if __name__ == "__main__":
    unittest.main()
        