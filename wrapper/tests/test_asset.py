import sys
import os
import time
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import numpy as np

from Exchange import Exchange
from Strategy import *
from helpers import *
from FastTest import FastTest

class AssetTestMethods(unittest.TestCase):

    def test_asset_load_csv(self):
        exchange = Exchange()
        broker = Broker(exchange)
        ft = FastTest(broker)
        
        ft.register_exchange(exchange) 
        new_asset = ft.register_asset("test1")
        new_asset.set_format("%d-%d-%d", 0, 1)
        new_asset.load_from_csv(file_name_1)
        assert(True)
        
    def test_asset_load_df(self):
        exchange = Exchange()
        broker = Broker(exchange)
        ft = FastTest(broker)
        
        ft.register_exchange(exchange) 
    
        for index, df in enumerate([df1,df2]):
            new_asset = ft.register_asset("test1")
            new_asset.set_format("%d-%d-%d", 0, 1)
            new_asset.load_from_df(df)
            asset_index = new_asset.index()
            asset_data = new_asset.data()
            for i, date in enumerate(asset_index):
                if index == 0:
                    actual = test1_index[i].astype('datetime64[s]').astype('float32')
                else:
                    actual = test2_index[i].astype('datetime64[s]').astype('float32')
                assert(date - actual == 0)
            if index == 0:
                assert((asset_data[:,0] == test1_open).all())
                assert((asset_data[:,1] == test1_close).all())
            else:
                assert((asset_data[:,0] == test2_open).all())
                assert((asset_data[:,1] == test2_close).all())

    def test_asset_datetime_index(self):
        exchange = Exchange()
        broker = Broker(exchange)
        ft = FastTest(broker)
        
        ft.register_exchange(exchange) 
        for index, file_name in enumerate([file_name_1,file_name_2]):
            new_asset = ft.register_asset("test1")
            new_asset.set_format("%d-%d-%d", 0, 1)
            new_asset.load_from_csv(file_name)
            asset_index = new_asset.index()
            for i, date in enumerate(asset_index):
                if index == 0:
                    actual = test1_index[i].astype('datetime64[s]').astype('float32')
                else:
                    actual = test2_index[i].astype('datetime64[s]').astype('float32')
                assert(date - actual == 0)

    def test_asset_data(self):
        exchange = Exchange()
        broker = Broker(exchange)
        ft = FastTest(broker)
        
        ft.register_exchange(exchange) 
        for index, file_name in enumerate([file_name_1,file_name_2]):
            new_asset = ft.register_asset("test1")
            new_asset.set_format("%d-%d-%d", 0, 1)
            new_asset.load_from_csv(file_name)
            asset_data = new_asset.data()
            if index == 0:
                assert((asset_data[:,0] == test1_open).all())
                assert((asset_data[:,1] == test1_close).all())
            else:
                assert((asset_data[:,0] == test2_open).all())
                assert((asset_data[:,1] == test2_close).all())
                
    def test_asset_warmup(self, logging = False, debug = False):
        ft = FastTest(logging=logging, debug=debug)
        exchange = Exchange(logging = logging)
        ft.register_exchange(exchange)
        
        broker = Broker(exchange,logging=logging, debug=debug)
        ft.register_broker(broker)
        ft.add_account("default", 100000)

        for i, file_name in enumerate([file_name_1,file_name_2]):
            new_asset = ft.register_asset(str(i+1))
            new_asset.set_format("%d-%d-%d", 0, 1)
            new_asset.load_from_csv(file_name)
            if i == 1:
                new_asset.set_warmup(2)
                
        orders = [
                OrderSchedule(
                    order_type = OrderType.MARKET_ORDER,
                    asset_name = "2",
                    i = 0,
                    units = 100,
                    exchange_name = "default",
                    account_name = "default"
                )
            ]
        strategy = TestStrategy(orders, broker, exchange)
        ft.add_strategy(strategy)   
        ft.build()
        ft.run()
        
        position_history = broker.get_position_history()
        assert(position_history.POSITION_ARRAY[0].contents.position_create_time == 960336000)
        assert(position_history.POSITION_ARRAY[0].contents.average_price == 98)
        
    def test_generate_random(self):
        ft = FastTest(logging=False, debug=False)
        exchange = Exchange(logging = False)
        ft.register_exchange(exchange)
        
        broker = Broker(exchange,logging=False, debug=False)
        ft.register_broker(broker)
        ft.add_account("default", 100000)
        
        for i in range(0,5):
            new_asset = ft.register_asset(str(i))
            new_asset.set_format("%d-%d-%d", 0, 0)
            new_asset_df = new_asset.generate_random(step_size = .01, num_steps = 1000)
            new_asset.load_from_df(new_asset_df, nano = True)
            
        ft.build()
        ft.run()
        
        datetime_epoch_index = ft.get_datetime_index()
        datetime_epoch_index_actual = pd.date_range(end='1/1/2020', periods=1000, freq = "s").values.astype(np.float64)
        assert(np.array_equal(datetime_epoch_index, datetime_epoch_index_actual/1e9))

if __name__ == '__main__':
    unittest.main()