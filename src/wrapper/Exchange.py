import sys
from ctypes import *
from Asset import Asset
import LibWrapper
import numpy as np

class Exchange():
    def __init__(self, logging = False) -> None:
        self.ptr = LibWrapper._new_exchange_ptr(logging)
        self.asset_names = []

    def __del__(self):
        LibWrapper._free_exchange_ptr(self.ptr)

    def reset(self):
        LibWrapper._reset_exchange(self.ptr)

    def register_asset(self, asset : Asset):
        self.asset_names.append(asset.asset_name)
        LibWrapper._register_asset(asset.ptr, self.ptr)

    def build(self):
        LibWrapper._build_exchange(self.ptr)

    def get_market_price(self, asset_name : str, on_close = True):
        return LibWrapper._get_market_price(
            self.ptr, 
            c_char_p(asset_name.encode("utf-8")),
            c_bool(on_close)
        )
        
    def get_asset_data(self, asset_name : str):
        asset_ptr = LibWrapper._get_asset_ptr(self.ptr, c_char_p(asset_name.encode("utf-8")) )
        return Asset._data(asset_ptr)
        
    def get_market_view(self):
        LibWrapper._get_market_view(self.ptr)

    def asset_count(self):
        return LibWrapper._asset_count(self.ptr)
    
if __name__ == "__main__":
    pass