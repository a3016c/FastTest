import sys
import os
import time
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import numpy as np
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
                        1,
                        False
                    )
            else:
                if(fast < slow):
                    Wrapper._place_market_order(
                        self.broker_ptr,
                        asset_id,
                        -1,
                        False
                    )                 
        
class AssetTestMethods(unittest.TestCase):

    def test_strat_construction(self):
        exchange, broker, ft = setup_multi()
        assert(exchange.asset_count() == 2)
        assert(exchange.asset_counter == 2)
        assert(exchange.ptr == ft.exchange.ptr)
        assert(broker.ptr == ft.broker.ptr)
        
    def test_benchmark_strategy(self):
        exchange, broker, ft = setup_multi(False)
        strategy = BenchMarkStrategy(broker.ptr, exchange.ptr)
        ft.add_strategy(strategy)
        ft.run()
        
        order_history = broker.get_order_history()
        position_history = broker.get_position_history()
        assert(len(order_history) == 2)
        assert(len(position_history) == 2)
        assert(order_history.ORDER_ARRAY[0].contents.fill_price == 101.5)
        assert(order_history.ORDER_ARRAY[1].contents.fill_price == 101)
        assert(position_history.POSITION_ARRAY[0].contents.close_price == 106)
        assert(position_history.POSITION_ARRAY[1].contents.close_price == 96)
        
        assert((broker.get_cash_history()==np.array([100000,  89850,  79750,  79750,  90350,  99950])).all())
        assert((broker.get_nlv_history()==np.array([100000,  99750,  99750, 100400, 100500,  99950])).all())

    def test_ma_cross(self):
        COLUMNS = ['OPEN','CLOSE']
        CANDLES = 20000
        STOCKS = 100
        dateindex = pd.date_range(start='2010-01-01', periods=CANDLES, freq='15Min')

        exchange = Exchange()
        broker = Broker(exchange)
        ft = FastTest(exchange, broker, False)
        for i in range(STOCKS):

            data = np.random.randint(10, 20, size=(CANDLES, len(COLUMNS)))
            df = pd.DataFrame(data * 1.01, dateindex, columns=COLUMNS)
            df = df.rename_axis('datetime')
            df["10"] = df["CLOSE"].rolling(10).mean()
            df["50"] = df["CLOSE"].rolling(50).mean()
            df.dropna(inplace = True)
            
            new_asset = Asset(exchange, asset_name=str(i+1))
            new_asset.set_format("%d-%d-%d", 0, 1)
            new_asset.load_from_df(df)
            ft.exchange.register_asset(new_asset)
    
        ft.build()
        strategy = MA_Cross(broker, exchange, 10, 50)
        ft.add_strategy(strategy)
        st = time.time()
        ft.profile()
        et = time.time()
        print("=========SIMPLE RUN=========")
        print(f"FastTest run in: {(et-st):.2f} Seconds")
        print(f"Candles Per Second: {CANDLES*STOCKS/(et-st):,.2f}")
        print("============================")        
        order_history = broker.get_order_history()
        position_history = broker.get_position_history()
        
        print(position_history.to_df())
        
if __name__ == '__main__':
    unittest.main()

