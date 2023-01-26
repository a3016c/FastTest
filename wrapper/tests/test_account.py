import sys
import os
import unittest

import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from Exchange import Exchange, Asset
from Broker import Broker
from Strategy import *
from FastTest import FastTest
from helpers import *


class AccountTestMethods(unittest.TestCase):
    
    def test_multi_account_setup(self):
        print("TESTING test_multi_account_setup...")
        exchange, broker, ft = setup_multi_account(logging=False, debug=False)
        ft.run()
        assert(True)
        print("TESTING: test_multi_account_setup passed")

    def test_multi_account(self):
        print("TESTING test_multi_account...")
        orders = [
                OrderSchedule(
                    order_type = OrderType.MARKET_ORDER,
                    asset_name = "1",
                    i = 0,
                    units = 100,
                    account_name = "account1"
                ),
                OrderSchedule(
                    order_type = OrderType.LIMIT_ORDER,
                    asset_name = "2",
                    i = 1,
                    units = -100,
                    limit = 101,
                    account_name = "account2"
                )
            ]
        exchange, broker, ft = setup_multi_account(logging=False, debug=False)
        strategy = TestStrategy(orders, broker, exchange)
        
        ft.add_strategy(strategy)
        ft.run()
        
        act_1_nlv = ft.accounts["account1"].get_nlv_history()
        act_2_nlv = ft.accounts["account2"].get_nlv_history()
        nlv = broker.get_nlv_history()
        
        assert(np.array_equal(act_1_nlv,np.array([100000,  100100,  100300, 100500, 100600,  100600])))
        assert(np.array_equal(act_2_nlv,np.array([100000, 100000, 100000,  99950,  99950, 100500])))
        assert(np.array_equal(nlv, act_1_nlv + act_2_nlv))
        print("TESTING: test_multi_account passed")
       
    def test_multi_account_id(self):
        print("TESTING test_multi_account_id...")
        orders1 = [
                OrderSchedule(
                    order_type = OrderType.MARKET_ORDER,
                    asset_name = "1",
                    i = 0,
                    units = 100,
                    exchange_name = "exchange1",
                    account_name = "default"
                )
            ]
        orders2 = [
                OrderSchedule(
                    order_type = OrderType.MARKET_ORDER,
                    asset_name = "2",
                    i = 0,
                    units = 100,
                    exchange_name = "exchange2",
                    account_name = "account2"
                )
         ]
        broker, ft = setup_multi_exchange(logging=False, debug=False, build=False)
        ft.add_account("account2", 100000)
        ft.build()
        
        strategy1 = TestStrategy(orders1, broker, exchange=None)
        strategy2 = TestStrategy(orders2, broker, exchange=None)
        ft.add_strategy(strategy1)
        ft.add_strategy(strategy2)
        ft.run()
        
        order_history = broker.get_order_history()
        position_history = broker.get_position_history()
        
        assert(position_history.POSITION_ARRAY[0].contents.asset_id == 0)
        assert(position_history.POSITION_ARRAY[1].contents.asset_id == 1)
        
        assert(position_history.POSITION_ARRAY[0].contents.exchange_id == 0)
        assert(position_history.POSITION_ARRAY[1].contents.exchange_id == 1)
        
        assert(position_history.POSITION_ARRAY[0].contents.account_id == 0)
        assert(position_history.POSITION_ARRAY[1].contents.account_id == 1)
        
        assert(position_history.POSITION_ARRAY[0].contents.strategy_id == 0)
        assert(position_history.POSITION_ARRAY[1].contents.strategy_id == 1)
        
        act_1_nlv = ft.accounts["default"].get_nlv_history()
        act_2_nlv = ft.accounts["account2"].get_nlv_history()
        nlv = broker.get_nlv_history()
        
        assert(np.array_equal(act_1_nlv,np.array([100000,  100100,  100300, 100500, 100600,  100600])))        
        assert(np.array_equal(act_2_nlv,np.array([100000,  99900,  99700, 100150, 100150,  99600])))
        assert(np.array_equal(nlv, act_1_nlv + act_2_nlv))
        print("TESTING: test_multi_account passed")
        
if __name__ == '__main__':
    unittest.main()



        