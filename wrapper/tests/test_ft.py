import sys
import os
import time
import unittest
import faulthandler
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import numpy as np
from Exchange import Exchange, Asset
from Broker import Broker
from Strategy import *
from FastTest import FastTest
from helpers import *

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
        
if __name__ == '__main__':
    unittest.main()

