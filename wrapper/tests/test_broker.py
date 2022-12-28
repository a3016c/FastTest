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
from helpers import *

class AssetTestMethods(unittest.TestCase):

    def test_broker_load(self):
        exchange = Exchange()
        broker = Broker(exchange)
        ft = FastTest(exchange, broker)

        new_asset = Asset(exchange, asset_name="1")
        new_asset.set_format("%d-%d-%d", 0, 1)
        new_asset.load_from_csv(file_name_2)
        ft.exchange.register_asset(new_asset)
        
        ft.build()
        strategy = Strategy(broker, exchange)
        ft.add_strategy(strategy)
        ft.run()

    def test_limit_order(self):
        exchange, broker, ft = setup_multi()
        orders = [
            OrderSchedule(
                order_type = OrderType.LIMIT_ORDER,
                asset_name = "2",
                i = 0,
                units = 100,
                limit = 97
            )
        ]
        strategy = TestStrategy(orders, broker, exchange)
        ft.add_strategy(strategy)
        ft.run()
        
        order_history = broker.get_order_history()
        position_history = broker.get_position_history()
        assert(len(order_history) == 1)
        assert(len(position_history) == 1)
        
        assert(order_history.ORDER_ARRAY[0].contents.fill_price == 97)
        assert(position_history.POSITION_ARRAY[0].contents.average_price == 97)
        print(position_history.POSITION_ARRAY[0].contents.close_price)
        

if __name__ == '__main__':
    unittest.main()

