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
                
if __name__ == '__main__':
    unittest.main()



        