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

class StrategyTestMethods(unittest.TestCase):
    
    def test_multi_strat(self):
        print("TESTING test_multi_strat...")
        orders1 = [
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
        orders2 = [
                OrderSchedule(
                    order_type = OrderType.MARKET_ORDER,
                    asset_name = "2",
                    i = 1,
                    units = 50
                ),
                OrderSchedule(
                    order_type = OrderType.MARKET_ORDER,
                    asset_name = "2",
                    i = 3,
                    units = -50
                )
         ]
                
        exchange, broker, ft = setup_multi(logging=False, margin=True, debug=False)
        strategy1 = TestStrategy(orders1, broker, exchange, strategy_name="strategy1")
        strategy2 = TestStrategy(orders2, broker, exchange, strategy_name="strategy2")
        ft.add_strategy(strategy1)
        ft.add_strategy(strategy2)
        ft.run()
        
        order_history = broker.get_order_history()
        position_history = broker.get_position_history()
        assert(len(order_history) == 4)
        assert(len(position_history) == 1)
                
        assert(order_history.ORDER_ARRAY[0].contents.strategy_id == 0)
        assert(order_history.ORDER_ARRAY[1].contents.strategy_id == 1)
        assert(order_history.ORDER_ARRAY[2].contents.strategy_id == 0)
        assert(order_history.ORDER_ARRAY[3].contents.strategy_id == 1)
        
        assert(np.array_equal(broker.get_nlv_history(),np.array([100000,  99900,  99650, 100300, 100275,  100000])))
        assert(np.array_equal(broker.get_cash_history(),np.array([100000,   94950,   92375,   95225,   97737.5, 100000])))
    
        print("TESTING: test_multi_strat passed")
        
if __name__ == '__main__':
    unittest.main()
