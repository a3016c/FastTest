import sys
import os
import time
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import numpy as np
from Asset import Asset
from Broker import Broker
from Strategy import *
from FastTest import FastTest
from constants import *

class AssetTestMethods(unittest.TestCase):

    def test_asset_load_csv(self):
        new_asset = Asset(asset_name="test1")
        new_asset.set_format("%d-%d-%d", 0, 1)
        new_asset.load_from_csv(file_name_1)
        
        ft = FastTest()
        ft.build()
        strategy = BenchMarkStrategy()
        ft.add_strategy(strategy)
        ft.run()

if __name__ == '__main__':
    unittest.main()

