import sys
import os
import time
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import numpy as np
from Exchange import Exchange, Asset
from constants import *
import FastTest

class AssetTestMethods(unittest.TestCase):

    def test_asset_load_csv(self):
        exchange = Exchange()
        new_asset = Asset(exchange, asset_name="test1")
        new_asset.set_format("%d-%d-%d", 0, 1)
        new_asset.load_from_csv(file_name_1)
        assert(True)

    def test_asset_datetime_index(self):
        exchange = Exchange()
        for index, file_name in enumerate([file_name_1,file_name_2]):
            new_asset = Asset(exchange, asset_name="test1")
            new_asset.set_format("%d-%d-%d", 0, 1)
            new_asset.load_from_csv(file_name)
            asset_index = new_asset.index()
            for i in range(len(asset_index)):
                if index == 0:
                    actual = test1_index[i].astype('datetime64[s]').astype('float32')
                else:
                    actual = test2_index[i].astype('datetime64[s]').astype('float32')
                idx = asset_index[i]
                assert(actual - idx == 0)

    def test_asset_data(self):
        exchange = Exchange()
        for index, file_name in enumerate([file_name_1,file_name_2]):
            new_asset = Asset(exchange, asset_name="test1")
            new_asset.set_format("%d-%d-%d", 0, 1)
            new_asset.load_from_csv(file_name)
            asset_data = new_asset.data()
            if index == 0:
                assert((asset_data[:,0] == test1_open).all())
                assert((asset_data[:,1] == test1_close).all())
            else:
                assert((asset_data[:,0] == test2_open).all())
                assert((asset_data[:,1] == test2_close).all())
    

if __name__ == '__main__':
    unittest.main()

