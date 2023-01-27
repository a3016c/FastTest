import sys
import os
from ctypes import c_char_p

import unittest
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from Exchange import Exchange, Asset
from Broker import Broker
from Strategy import *
from FastTest import FastTest
import Wrapper
from helpers import *

class MA_Cross(Strategy):
    def __init__(self, broker: Broker, exchange: Exchange, slow_ma : int, fast_ma : int) -> None:
        super().__init__(broker, exchange)
        self.slow_ma = c_char_p(str(slow_ma).encode("utf-8"))
        self.fast_ma = c_char_p(str(fast_ma).encode("utf-8"))
        self.exchange_ptr = exchange.ptr
        self.broker_ptr = broker.ptr
        
    def build(self):
        self.asset_ids = self.exchange.asset_map.values()
        
    def next(self):
        for asset_id in self.asset_ids:
            fast = Wrapper._get_market_feature(self.exchange_ptr, asset_id, self.fast_ma, 0)
            slow = Wrapper._get_market_feature(self.exchange_ptr, asset_id, self.slow_ma, 0)
            
            if(not Wrapper._position_exists(self.broker_ptr, asset_id)):
                if(fast > slow):
                    Wrapper._place_market_order(
                        self.broker_ptr,
                        asset_id,
                        10,
                        False
                    )
            else:
                if(fast < slow):
                    Wrapper._place_market_order(
                        self.broker_ptr,
                        asset_id,
                        -10,
                        False
                    )                 
        
class FTTestMethods(unittest.TestCase):

    def test_strat_construction(self):
        exchange, broker, ft = setup_multi()
        assert(exchange.asset_count() == 2)
        assert(exchange.asset_counter == 2)
        assert(broker.ptr == ft.broker.ptr)
        
    """
    def test_benchmark_strategy(self):
        exchange, broker, ft = setup_multi(debug=True)
        strategy = BenchMarkStrategy(broker.ptr, exchange.ptr)
        ft.add_strategy(strategy)
        ft.run()
                
        order_history = broker.get_order_history()
        position_history = broker.get_position_history()
        
        print(order_history.to_df())
        
        assert(len(order_history) == 2)
        assert(len(position_history) == 2)
        assert(order_history.ORDER_ARRAY[0].contents.fill_price == 101.5)
        assert(order_history.ORDER_ARRAY[1].contents.fill_price == 101)
        assert(position_history.POSITION_ARRAY[0].contents.close_price == 106)
        assert(position_history.POSITION_ARRAY[1].contents.close_price == 96)
        
        assert((broker.get_cash_history()==np.array([100000,  89850,  79750,  79750,  90350,  99950])).all())
        assert((broker.get_nlv_history()==np.array([100000,  99750,  99750, 100400, 100500,  99950])).all())
    """
    def test_ma_cross(self):
        COLUMNS = ['OPEN','CLOSE']
        CANDLES = 2000
        STOCKS = 10
        dateindex = pd.date_range(start='2010-01-01', periods=CANDLES, freq='15Min')

        ft = FastTest(debug = False)
        
        exchange = Exchange()
        ft.register_exchange(exchange)
        
        broker = Broker(exchange)
        ft.register_broker(broker)
        
        for i in range(STOCKS):

            data = np.random.randint(10, 20, size=(CANDLES, len(COLUMNS)))
            df = pd.DataFrame(data * 1.01, dateindex, columns=COLUMNS)
            df = df.rename_axis('datetime')
            df["10"] = df["CLOSE"].rolling(10).mean()
            df["50"] = df["CLOSE"].rolling(50).mean()
            df.dropna(inplace = True)
            
            new_asset = ft.register_asset(str(i+1))
            new_asset.set_format("%d-%d-%d", 0, 1)
            new_asset.load_from_df(df)
            
        ft.build()
        strategy = MA_Cross(broker, exchange, 10, 50)
        ft.add_strategy(strategy)
        ft.run()
        
    def test_benchmark_asset(self):
        exchange, broker, ft = setup_multi(False)
        
        benchmark = Asset(exchange.exchange_id, asset_name=str("Benchmark"))
        ft.register_benchmark(benchmark)
        benchmark.set_format("%d-%d-%d", 0, 1)
        benchmark.load_from_csv(file_name_2)
        
        benchmark = ft.benchmark.df()
        assert((benchmark["CLOSE"].values == test2_close).all())
        
    def test_get_last_positions(self):
        orders = [
                OrderSchedule(
                    order_type = OrderType.MARKET_ORDER,
                    asset_name = "2",
                    i = 0,
                    units = 100,
                    exchange_name = "default",
                    account_name = "account1"
                ),
         ]
        exchange, broker, ft = setup_multi_account(logging=False, debug=False, save_last_positions=True)
        strategy1 = TestStrategy(orders, broker, exchange=None)
        ft.add_strategy(strategy1)
        ft.run()
        
        last_positions = ft.get_last_positions()
        assert(last_positions.number_positions == 1)
        assert(last_positions.POSITION_ARRAY[0].contents.close_price == 0)
        assert(last_positions.POSITION_ARRAY[0].contents.realized_pl == 0)
        assert(last_positions.POSITION_ARRAY[0].contents.unrealized_pl == -400)
            
if __name__ == '__main__':
    unittest.main()

