import unittest
import pandas as pd 
import numpy as np
import sys

sys.path.insert(1, "src")

from FastTest import FastTest
from Exchange import Exchange
from Broker import Broker
from Strategy import Strategy
from Asset import Asset
from Order import *

class TestSimple(unittest.TestCase):
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
        
    def test_fasttest_run(self):
        """
        Test:
        take no actions. Verify FastTest run() displaying exchange views as expected
        """
        self.exchange.reset()
        self.broker.reset()
        
        class BasicStrategy(Strategy):
            def __init__(self, exchange: Exchange, broker: Broker) -> None:
                super().__init__(exchange, broker)

            def next(self):
                exchange_view = self.exchange.market_view
                if self.exchange.market_time == pd.to_datetime("2000-06-06"):
                    assert(exchange_view["test1"]["OPEN"]==100)
                    assert(exchange_view["test1"]["CLOSE"]==101)
                    assert(exchange_view["test2"]["OPEN"]==100)
                    assert(exchange_view["test2"]["CLOSE"]==99)

                elif self.exchange.market_time == pd.to_datetime("2000-06-07"):
                    assert(exchange_view["test1"]["OPEN"]==102)
                    assert(exchange_view["test1"]["CLOSE"]==103)
                    assert(exchange_view["test2"]["OPEN"]==98)
                    assert(exchange_view["test2"]["CLOSE"]==97)

                elif self.exchange.market_time == pd.to_datetime("2000-06-08"):
                    assert(exchange_view["test1"]["OPEN"]==104)
                    assert(exchange_view["test1"]["CLOSE"]==105)
                    assert(exchange_view["test2"]["OPEN"]==96)
                    assert(exchange_view["test2"]["CLOSE"]==95)

                return []

        strategy = BasicStrategy(
            exchange=self.exchange,
            broker=self.broker
        )
        self.fast_test.register_strategy(strategy)
        self.fast_test.run()

    def test_market_order(self):
        """
        Test:
        buy 100 shares of test1 at first available open and hold till last close
        """
        self.exchange.reset()
        self.broker.reset()
        
        class BasicStrategy(Strategy):
            def __init__(self, exchange: Exchange, broker: Broker) -> None:
                self.counter = 1
                super().__init__(exchange, broker)

            def next(self):
                if self.counter == 1:
                    self.counter += 1
                    new_order = MarketOrder(
                        order_create_time = self.exchange.market_time,
                        asset_name = "test1",
                        units = 100
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

        assert(self.fast_test.portfolio_value_history == [100000,100100,100300,100400])
        assert(strategy_analysis["test1"]["number_trades"] == 1)
        assert(strategy_analysis["test1"]["win_rate"] == 1.0)
        assert(strategy_analysis["test1"]["time_in_market"] == np.timedelta64(3,"D"))
        
        assert(strategy_analysis["test2"]["number_trades"] == 0)
        assert(strategy_analysis["test2"]["win_rate"] == 0)
        assert(strategy_analysis["test2"]["time_in_market"] == np.timedelta64(0,"D"))
        
        assert(str(position_history[0].position_open_time) == "2000-06-07 00:00:00")
        assert(str(position_history[0].position_close_time) == "2000-06-09 00:00:00")
        assert(position_history[0].average_price == 102)
        assert(position_history[0].close_price == 106)
        assert(position_history[0].unrealized_pl == 0)
        assert(position_history[0].realized_pl == 400)

    def test_market_order_sell(self):
        """
        Test:
        buy 100 shares of test1 at first available open and sell the next period.
        buy will be executed at second period open, we then read the second period data and 
        determine that we want to sell, which will be executed at the third period open. 
        """
        self.exchange.reset()
        self.broker.reset()
        
        class BasicStrategy(Strategy):
            def __init__(self, exchange: Exchange, broker: Broker) -> None:
                self.counter = 0
                super().__init__(exchange, broker)

            def next(self):
                self.counter += 1
                if self.counter == 1: 
                    new_order = MarketOrder(
                        order_create_time = self.exchange.market_time,
                        asset_name = "test1",
                        units = 100
                    )
                    return [new_order]
                elif self.counter == 2:
                    new_order = MarketOrder(
                        order_create_time = self.exchange.market_time,
                        asset_name = "test1",
                        units = -100
                    )
                    return [new_order]
        
        strategy = BasicStrategy(
            exchange=self.exchange,
            broker=self.broker
        )
        self.fast_test.register_strategy(strategy)
        self.fast_test.run()  

        strategy_analysis = self.broker.strategy_analysis
        position_history = self.broker.position_history

        print(strategy_analysis)
        assert(self.fast_test.portfolio_value_history == [100000,100100,100200,100200])
        assert(strategy_analysis["test1"]["number_trades"] == 1)
        assert(strategy_analysis["test1"]["win_rate"] == 1.0)
        assert(strategy_analysis["test1"]["time_in_market"] == np.timedelta64(1,"D"))
        
        assert(str(position_history[0].position_open_time) == "2000-06-07 00:00:00")
        assert(str(position_history[0].position_close_time) == "2000-06-08 00:00:00")
        assert(position_history[0].average_price == 102)
        assert(position_history[0].close_price == 104)
        assert(position_history[0].unrealized_pl == 0)
        assert(position_history[0].realized_pl == 200)


if __name__ == "__main__":
    unittest.main()