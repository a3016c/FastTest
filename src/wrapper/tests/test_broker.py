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
from constants import *

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
        strategy = Strategy(broker.ptr, exchange.ptr)
        ft.add_strategy(strategy)
        ft.run()

if __name__ == '__main__':
    unittest.main()

