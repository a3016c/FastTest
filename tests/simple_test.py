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
                    assert(exchange_view["test2"]["OPEN"]==101)
                    assert(exchange_view["test2"]["CLOSE"]==101.5)

                return []

        strategy = BasicStrategy(
            exchange=self.exchange,
            broker=self.broker
        )
        self.fast_test.register_strategy(strategy)
        self.fast_test.run()

    def test_market_order_buy(self):
        """
        Test:
        buy 100 shares of test1 at first available open and hold till last close
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

        assert(self.fast_test.portfolio_value_history["net_liquidation_value"].values.tolist() == [100000,100000,100100,100300,100400,100400])
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
        buy 100 shares of test1 at first available open. Order placed on 2000-06-06 executed at open next day.
        sell 100 shares on 2000-06-08 order will be placed on 2000-06-07
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
                        units = 100
                    )
                    return [new_order]
                elif str(current_time.date()) == "2000-06-07":
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

        assert(self.fast_test.portfolio_value_history["net_liquidation_value"].values.tolist() == [100000, 100000, 100100, 100200, 100200, 100200])
        assert(strategy_analysis["test1"]["number_trades"] == 1)
        assert(strategy_analysis["test1"]["win_rate"] == 1.0)
        assert(strategy_analysis["test1"]["time_in_market"] == np.timedelta64(1,"D"))

        assert(str(position_history[0].position_open_time) == "2000-06-07 00:00:00")
        assert(str(position_history[0].position_close_time) == "2000-06-08 00:00:00")
        assert(position_history[0].average_price == 102)
        assert(position_history[0].close_price == 104)
        assert(position_history[0].unrealized_pl == 0)
        assert(position_history[0].realized_pl == 200)

    def test_market_order_multi_asset(self):
        """
        Test:
        buy 100 shares of test1 on 2000-06-08 at open (order placed on close on 2000-06-07) and hold till last close
        buy 100 shares of test2 on 2000-06-06 at open (order place on close on 2000-06-05) and sell at open on 2000-06-12 (order placed on 2000-06-09)
        """
        self.exchange.reset()
        self.broker.reset()
        
        class BasicStrategy(Strategy):
            def __init__(self, exchange: Exchange, broker: Broker) -> None:
                super().__init__(exchange, broker)

            def next(self):
                current_time = self.exchange.market_time
                if str(current_time.date()) == "2000-06-05":
                    new_order = MarketOrder(
                        order_create_time = current_time,
                        asset_name = "test2",
                        units = 100
                    )
                    return [new_order] 
                elif str(current_time.date()) == "2000-06-07":
                    new_order = MarketOrder(
                        order_create_time = current_time,
                        asset_name = "test1",
                        units = 100
                    )
                    return [new_order]
                elif str(current_time.date()) == "2000-06-09":
                    new_order = MarketOrder(
                        order_create_time = current_time,
                        asset_name = "test2",
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

        assert(self.fast_test.portfolio_value_history["net_liquidation_value"].values.tolist() == [100000, 99900, 99700, 100250, 100350, 100500])
        assert(strategy_analysis["test1"]["number_trades"] == 1)
        assert(strategy_analysis["test1"]["win_rate"] == 1.0)
        assert(strategy_analysis["test1"]["time_in_market"] == np.timedelta64(2,"D"))

        assert(strategy_analysis["test2"]["number_trades"] == 1)
        assert(strategy_analysis["test2"]["win_rate"] == 1.0)
        assert(strategy_analysis["test2"]["time_in_market"] == np.timedelta64(4,"D"))

        assert(str(position_history[0].position_open_time) == "2000-06-08 00:00:00")
        assert(str(position_history[0].position_close_time) == "2000-06-09 00:00:00")
        assert(position_history[0].average_price == 104)
        assert(position_history[0].close_price == 106)
        assert(position_history[0].unrealized_pl == 0)
        assert(position_history[0].realized_pl == 200)

        assert(str(position_history[1].position_open_time) == "2000-06-06 00:00:00")
        assert(str(position_history[1].position_close_time) == "2000-06-12 00:00:00")
        assert(position_history[1].average_price == 100)
        assert(position_history[1].close_price == 103)
        assert(position_history[1].unrealized_pl == 0)
        assert(position_history[1].realized_pl == 300)

    def test_ma_cross(self):
        exchange = Exchange()
        broker = Broker(exchange=exchange)

        fast_ma = 20
        slow_ma = 50

        source_type = "csv"
        datetime_format = "%Y-%m-%d"
        datetime_column = "DATE"
        exchange.register_asset(Asset(
            "AAPL",
            source_type = "csv",
            csv_path = r"C:\Users\bktor\Desktop\Python\FastTest\tests\data\AAPL.csv",
            datetime_format = datetime_format,
            datetime_column = datetime_column,
            warmup = slow_ma-1,
            frequency = "1D"
            )
        )
        class BasicMovingAverageStrategy(Strategy):
            def __init__(self, exchange: Exchange, broker: Broker) -> None:
                super().__init__(exchange, broker)

            def next(self):
                position = self.broker.portfolio.get("AAPL")
                sma_fast = self.exchange.market_view["AAPL"][f"sma_{fast_ma}"]
                sma_slow = self.exchange.market_view["AAPL"][f"sma_{slow_ma}"]

                if position == None:
                    if sma_fast > sma_slow:
                        new_order = MarketOrder(
                            order_create_time = self.exchange.market_time,
                            asset_name = "AAPL",
                            units = 100
                        )
                        return [new_order]
                else:
                    if sma_fast < sma_slow:
                        new_order = MarketOrder(
                            order_create_time = self.exchange.market_time,
                            asset_name = "AAPL",
                            units = -100
                        )
                        return [new_order]

        strategy = BasicMovingAverageStrategy(
                    exchange=exchange,
                    broker=broker
                )
        fast_test = FastTest(
            exchange=exchange,
            broker=broker
        )
        fast_test.register_strategy(strategy)
        fast_test.run()

        strategy_analysis = broker.strategy_analysis
        position_history = broker.position_history
        portfolio_value_history = fast_test.portfolio_value_history

        df_test = portfolio_value_history
        df_test = pd.merge(df_test,fast_test.exchange.market["AAPL"].df, left_index=True,right_index=True)

        def get_next_trading_day(x):
            current_idx = df_test.index.get_loc(x)
            if current_idx == len(df_test): return x
            return df_test.index[current_idx+1]

        df_test["fast_above_slow"] = df_test["sma_20"] > df_test["sma_50"]
        df_test["previous_fast_above_slow"] = df_test["fast_above_slow"].shift(1)
        df_test["previous_fast_above_slow"].loc[df_test.index[0]] = not df_test["fast_above_slow"].loc[df_test.index[0]]
        df_test_buy = df_test[(df_test["fast_above_slow"] == True) & (df_test["previous_fast_above_slow"] == False)]
        df_test_sell = df_test[(df_test["fast_above_slow"] == False) & (df_test["previous_fast_above_slow"] == True)]
        df_test_sell.drop(df_test_sell.index[:1], inplace=True)

        df_test_evaluation = pd.DataFrame(data=[df_test_buy.index,df_test_sell.index]).T
        df_test_evaluation.columns = ["signal_date_buy","signal_date_sell"]
        df_test_evaluation["purchase_date"], df_test_evaluation["sale_date"] = df_test_evaluation["signal_date_buy"].apply(get_next_trading_day), df_test_evaluation["signal_date_sell"].apply(get_next_trading_day)

        for index, row in df_test_evaluation.iterrows():
            position_check = position_history[index]
            purchase_date = row["purchase_date"]
            sale_date = row["sale_date"]
            purchase_price = df_test.loc[purchase_date]["OPEN"]

            if sale_date < df_test.index[-1]: sale_price = df_test.loc[sale_date]["OPEN"]
            else: sale_price = df_test.loc[sale_date]["CLOSE"]
            
            assert(position_check.average_price == purchase_price)
            assert(position_check.close_price == sale_price)
            assert(position_check.position_open_time == purchase_date)
            assert(position_check.position_close_time == sale_date)

    def test_benchmark(self):
        self.exchange.reset()
        self.broker.reset()
        
        class BasicStrategy(Strategy):
            def __init__(self, exchange: Exchange, broker: Broker) -> None:
                super().__init__(exchange, broker)

            def next(self):
                current_time = self.exchange.market_time
                if str(current_time.date()) == "2000-06-05":
                    new_order = MarketOrder(
                        order_create_time = current_time,
                        asset_name = "test2",
                        units = 100
                    )
                    return [new_order] 
                elif str(current_time.date()) == "2000-06-07":
                    new_order = MarketOrder(
                        order_create_time = current_time,
                        asset_name = "test1",
                        units = 100
                    )
                    return [new_order]
                elif str(current_time.date()) == "2000-06-09":
                    new_order = MarketOrder(
                        order_create_time = current_time,
                        asset_name = "test2",
                        units = -100
                    )
                    return [new_order]
                else:
                    return []

        strategy = BasicStrategy(
            exchange=self.exchange,
            broker=self.broker
        )
        benchmark = BenchMarkBH(
            exchange=self.exchange,
            asset_name="test2"
        )

        self.fast_test.register_strategy(strategy)
        self.fast_test.register_benchmark(strategy = benchmark)
        self.fast_test.run()  

        strategy_analysis = self.broker.strategy_analysis
        position_history = self.broker.position_history
        portfolio_value_history = self.fast_test.portfolio_value_history

        assert(len(benchmark.broker.position_history) == 1)
        assert(benchmark.broker.position_history[0].average_price == 101.5)
        assert(benchmark.broker.position_history[0].close_price == 96)
        assert(benchmark.broker.net_liquidation_value==94581.28078817733)

        assert(self.fast_test.portfolio_value_history["net_liquidation_value"].values.tolist() == [100000, 99900, 99700, 100250, 100350, 100500])
        assert(strategy_analysis["test1"]["number_trades"] == 1)
        assert(strategy_analysis["test1"]["win_rate"] == 1.0)
        assert(strategy_analysis["test1"]["time_in_market"] == np.timedelta64(2,"D"))

        assert(strategy_analysis["test2"]["number_trades"] == 1)
        assert(strategy_analysis["test2"]["win_rate"] == 1.0)
        assert(strategy_analysis["test2"]["time_in_market"] == np.timedelta64(4,"D"))

        assert(str(position_history[0].position_open_time) == "2000-06-08 00:00:00")
        assert(str(position_history[0].position_close_time) == "2000-06-09 00:00:00")
        assert(position_history[0].average_price == 104)
        assert(position_history[0].close_price == 106)
        assert(position_history[0].unrealized_pl == 0)
        assert(position_history[0].realized_pl == 200)

        assert(str(position_history[1].position_open_time) == "2000-06-06 00:00:00")
        assert(str(position_history[1].position_close_time) == "2000-06-12 00:00:00")
        assert(position_history[1].average_price == 100)
        assert(position_history[1].close_price == 103)
        assert(position_history[1].unrealized_pl == 0)
        assert(position_history[1].realized_pl == 300)
    
if __name__ == "__main__":
    unittest.main()