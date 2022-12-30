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
        for j in range(0,2):
            orders = [
                OrderSchedule(
                    order_type = OrderType.LIMIT_ORDER,
                    asset_name = "2",
                    i = j,
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
            assert(position_history.POSITION_ARRAY[0].contents.close_price == 96)
            
            assert(np.datetime64(position_history.POSITION_ARRAY[0].contents.position_create_time,"s") == test2_index[2])
            assert(np.datetime64(position_history.POSITION_ARRAY[0].contents.position_close_time,"s") == test2_index[-1])

    def test_limit_sell(self):
        orders = [
                OrderSchedule(
                    order_type = OrderType.LIMIT_ORDER,
                    asset_name = "2",
                    i = 1,
                    units = 100,
                    limit = 97
                ),
                OrderSchedule(
                    order_type = OrderType.LIMIT_ORDER,
                    asset_name = "2",
                    i = 3,
                    units = -100,
                    limit = 103
                )
            ]
        exchange, broker, ft = setup_multi()
        strategy = TestStrategy(orders, broker, exchange)
        ft.add_strategy(strategy)
        ft.run()
        
        order_history = broker.get_order_history()
        position_history = broker.get_position_history()
        assert(len(order_history) == 2)
        assert(len(position_history) == 1)
            
        assert(order_history.ORDER_ARRAY[0].contents.fill_price == 97)
        assert(position_history.POSITION_ARRAY[0].contents.average_price == 97)
        assert(position_history.POSITION_ARRAY[0].contents.close_price == 103)
        
        assert(np.datetime64(position_history.POSITION_ARRAY[0].contents.position_close_time,"s") == test2_index[-1])

    def test_stoploss(self):
        orders = [
                OrderSchedule(
                    order_type = OrderType.MARKET_ORDER,
                    asset_name = "2",
                    i = 0,
                    units = 100
                ),
                OrderSchedule(
                    order_type = OrderType.STOP_LOSS_ORDER,
                    asset_name = "2",
                    i = 1,
                    units = -100,
                    limit = 98
                )
            ]
        exchange, broker, ft = setup_multi(False)
        strategy = TestStrategy(orders, broker, exchange)
        ft.add_strategy(strategy)
        ft.run()
        
        order_history = broker.get_order_history()
        position_history = broker.get_position_history()
        assert(len(order_history) == 2)
        assert(len(position_history) == 1)
        
        assert(order_history.ORDER_ARRAY[0].contents.fill_price == 100)
        assert(position_history.POSITION_ARRAY[0].contents.average_price == 100)
        assert(position_history.POSITION_ARRAY[0].contents.close_price == 98)
        assert(np.datetime64(position_history.POSITION_ARRAY[0].contents.position_close_time,"s") == test2_index[2])
        print(position_history.to_df())
        
if __name__ == '__main__':
    unittest.main()

