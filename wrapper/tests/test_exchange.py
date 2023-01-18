import sys
import os
import time
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import numpy as np
from Broker import Broker
from FastTest import FastTest
from Exchange import Exchange, Asset
from Strategy import *
from helpers import *

class ExchangeTestMethods(unittest.TestCase):
    
    def test_exchange_build(self):
        print("TESTING test_exchange_build...")
        ft = FastTest()
        
        exchange = Exchange()
        ft.register_exchange(exchange)
        
        broker = Broker(exchange)
        ft.register_broker(broker)
        
        
        
        for i in range (0,6):
            new_asset = Asset(exchange, asset_name=str(i))
            new_asset.set_format("%d-%d-%d", 0, 1)
            new_asset.load_from_csv(file_name_2)
            exchange.register_asset(new_asset)

        ft.build()
        assert(list(exchange.asset_map.keys()) == ['0', '1', '2', '3', '4', '5'])
        for i in range(0,6):
            asset_data = exchange.get_asset_data(str(i))
            assert((asset_data[:,0] == test2_open).all())
            assert((asset_data[:,1] == test2_close).all())
            
        print("TESTING test_exchange_build passed")
            
    def test_exchange_slippage(self):
        print("TESTING test_exchange_slippage...")
        orders = [
                OrderSchedule(
                    order_type = OrderType.MARKET_ORDER,
                    asset_name = "2",
                    i = 1,
                    units = 100
                ),
                OrderSchedule(
                    order_type = OrderType.MARKET_ORDER,
                    asset_name = "2",
                    i = 3,
                    units = -100
                )
            ]
        exchange, broker, ft = setup_multi(logging=False)
        exchange.set_slippage(.01)
        strategy = TestStrategy(orders, broker, exchange)
        ft.add_strategy(strategy)
        ft.run()
        
        order_history = broker.get_order_history()
        assert((order_history.ORDER_ARRAY[0].contents.fill_price - (98*1.01)) < .001)
        assert((order_history.ORDER_ARRAY[1].contents.fill_price - (101*.99)) < .001)
        print("TESTING: test_exchange_slippage passed")
        
    def test_get_id_max(self):
        print("TESTING test_get_id_max...")
        orders = []
        exchange, broker, ft = setup_multi(logging=False)
        strategy = TestStrategy(orders, broker, exchange)
        ft.add_strategy(strategy)
        
        ft.step()
        ft.step()
        ids = exchange.get_id_max("CLOSE", 1)
        assert(exchange.id_map[ids[0]] == "2")
        ft.step()
        ids = exchange.get_id_max("CLOSE", 1)
        assert(exchange.id_map[ids[0]] == "1")
        
        print("TESTING: test_get_id_max passed")
        
if __name__ == '__main__':
    unittest.main()

