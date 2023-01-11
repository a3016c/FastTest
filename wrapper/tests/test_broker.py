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

class BrokerTestMethods(unittest.TestCase):

    def test_broker_load(self):
        print("TESTING test_broker_load...")
        exchange = Exchange()
        broker = Broker(exchange)
        ft = FastTest(broker)
        
        ft.register_exchange(exchange)
        
        new_asset = Asset(exchange, asset_name="1")
        new_asset.set_format("%d-%d-%d", 0, 1)
        new_asset.load_from_csv(file_name_2)
        
        exchange.register_asset(new_asset)
        
        ft.build()
        strategy = Strategy(broker, exchange)
        ft.add_strategy(strategy)
        ft.run()
        print("TESTING: test_broker_load passed")
        
    def test_limit_order(self):
        print("TESTING: test_limit_order...")
        exchange, broker, ft = setup_multi(logging=False, debug=False)
        for j in range(0,2):
            ft.reset()
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
        print("TESTING: test_limit_order passed")
        
    def test_limit_sell(self):
        print("TESTING test_limit_sell...")
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
        exchange, broker, ft = setup_multi(logging=False)
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
        print("TESTING: test_limit_sell passed")
        
    def test_stoploss(self):
        print("TESTING test_stoploss...")
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

        print("TESTING: test_stoploss passed")
        
    def test_short(self):
        print("TESTING test_short...")

        orders = [
                OrderSchedule(
                    order_type = OrderType.MARKET_ORDER,
                    asset_name = "2",
                    i = 0,
                    units = -100
                )
         ]
        exchange, broker, ft = setup_multi(False)
        strategy = TestStrategy(orders, broker, exchange)
        ft.add_strategy(strategy)
        ft.run()
        
        order_history = broker.get_order_history()
        position_history = broker.get_position_history()
        
        assert(len(order_history) == 1)
        assert(len(position_history) == 1)
        assert(position_history.POSITION_ARRAY[0].contents.realized_pl == 400)
        assert(np.array_equal(broker.get_nlv_history(),np.array([100000,  100100,  100300, 99850, 99850,  100400])))
        assert(np.array_equal(broker.get_cash_history(),np.array([100000,  110000,  110000, 110000, 110000,  100400])))
    
        print("TESTING: test_short passed")
    
    def test_margin_long(self):
        print("TESTING test_margin_long...")
        orders = [
                OrderSchedule(
                    order_type = OrderType.MARKET_ORDER,
                    asset_name = "2",
                    i = 0,
                    units = 100
                )
         ]
        exchange, broker, ft = setup_multi(logging=False, margin=True, debug=False)
        
        strategy = TestStrategy(orders, broker, exchange)
        ft.add_strategy(strategy)
        ft.run()
                
        assert(np.array_equal(broker.get_nlv_history(),np.array([100000,  99900,  99700, 100150, 100150,  99600])))
        assert(np.array_equal(broker.get_cash_history(),np.array([100000,  94950,  94850,  95075,  95075,  99600])))

        print("TESTING: test_margin_long passed")
        
    def test_margin_short(self):
        print("TESTING test_margin_short...")

        orders = [
                OrderSchedule(
                    order_type = OrderType.MARKET_ORDER,
                    asset_name = "2",
                    i = 0,
                    units = -100
                )
         ]
        exchange, broker, ft = setup_multi(logging=False, margin=True)
        
        strategy = TestStrategy(orders, broker, exchange)
        ft.add_strategy(strategy)
        ft.run()
        
        assert(np.array_equal(broker.get_nlv_history(),np.array([100000,  100100,  100300, 99850, 99850,  100400])))
        assert(np.array_equal(broker.get_cash_history(),np.array([100000,  95150,  95450,  94775,  94775,  100400])))

        print("TESTING: test_margin_short passed")
        
    def test_position_increase(self):
        print("TESTING test_position_increase...")
        orders = [
                OrderSchedule(
                    order_type = OrderType.MARKET_ORDER,
                    asset_name = "2",
                    i = 0,
                    units = 100
                ),
                OrderSchedule(
                    order_type = OrderType.MARKET_ORDER,
                    asset_name = "2",
                    i = 1,
                    units = 100
                )
         ]
        exchange, broker, ft = setup_multi(logging=False, margin=False)
        
        strategy = TestStrategy(orders, broker, exchange)
        ft.add_strategy(strategy)
        ft.run()
        
        order_history = broker.get_order_history()
        position_history = broker.get_position_history()
        assert(len(order_history) == 2)
        assert(len(position_history) == 1)
        
        assert(np.array_equal(broker.get_nlv_history(),np.array([100000,  99900,  99600, 100500, 100500,  99400])))
        assert(np.array_equal(broker.get_cash_history(),np.array([100000,  90000,  80200,  80200,  80200,  99400])))

        print("TESTING: test_position_increase passed")
        
    def test_position_reduce(self):
        print("TESTING test_position_reduce...")
        orders = [
                OrderSchedule(
                    order_type = OrderType.MARKET_ORDER,
                    asset_name = "2",
                    i = 0,
                    units = 100
                ),
                OrderSchedule(
                    order_type = OrderType.MARKET_ORDER,
                    asset_name = "2",
                    i = 2,
                    units = -50
                )
         ]
        exchange, broker, ft = setup_multi(logging=False, margin=False)
        
        strategy = TestStrategy(orders, broker, exchange)
        ft.add_strategy(strategy)
        ft.run()
        
        order_history = broker.get_order_history()
        position_history = broker.get_position_history()
        assert(len(order_history) == 2)
        assert(len(position_history) == 1)
        
        assert(np.array_equal(broker.get_cash_history(),np.array([100000,  90000,  90000,  95050,  95050,  99850])))
        assert(np.array_equal(broker.get_nlv_history(),np.array([100000,  99900,  99700, 100125, 100125,  99850])))
    
        print("TESTING: test_position_reduce passed")
           
    def test_multi_exchange(self):
        print("TESTING test_multi_exchange...")
        orders = [
                OrderSchedule(
                    order_type = OrderType.MARKET_ORDER,
                    asset_name = "1",
                    i = 0,
                    units = 100,
                    exchange_name = "exchange1"
                ),
                OrderSchedule(
                    order_type = OrderType.MARKET_ORDER,
                    asset_name = "2",
                    i = 0,
                    units = 50,
                    exchange_name = "exchange2"
                )
         ]
        
        broker, ft = setup_multi_exchange(logging=True, debug=False)
        strategy = TestStrategy(orders, broker, exchange=None)
        ft.add_strategy(strategy)
        ft.run()
        
        assert(np.array_equal(broker.get_cash_history(),np.array([100000,  85000,  85000,  85000,  95600,  100400])))
        assert(np.array_equal(broker.get_nlv_history(),np.array([100000, 100050, 100150, 100575, 100675, 100400])))
    
        print("TESTING: test_multi_exchange passed")

    
if __name__ == '__main__':
    unittest.main()

