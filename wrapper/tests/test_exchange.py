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

        

if __name__ == '__main__':
    unittest.main()

