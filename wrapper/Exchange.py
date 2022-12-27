import sys
from ctypes import *
import Wrapper
import numpy as np
import pandas as pd


class Exchange():
    def __init__(self, logging = False) -> None:
        self.ptr = Wrapper._new_exchange_ptr(logging)
        self.asset_map = {}
        self.asset_counter = 0

    def __del__(self):
        Wrapper._free_exchange_ptr(self.ptr)

    def reset(self):
        Wrapper._reset_exchange(self.ptr)

    def register_asset(self, asset):
        self.asset_map[asset.asset_name] = self.asset_counter
        Wrapper._register_asset(asset.ptr, self.ptr)
        self.asset_counter += 1

    def build(self):
        Wrapper._build_exchange(self.ptr)

    def get_market_price(self, asset_name : str, on_close = True):
        asset_id = self.asset_map[asset_name]
        return Wrapper._get_market_price(
            self.ptr, 
            asset_id,
            c_bool(on_close)
        )
        
    def get_asset_data(self, asset_name : str):
        asset_id = self.asset_map[asset_name]
        asset_ptr = Wrapper._get_asset_ptr(self.ptr,asset_id)
        return Asset._data(asset_ptr)
        
    def get_market_view(self):
        Wrapper._get_market_view(self.ptr)

    def asset_count(self):
        return Wrapper._asset_count(self.ptr)

class Asset():
    def __init__(self, exchange : Exchange, asset_name : str) -> None:
        self.asset_name = asset_name
        self.ptr = Wrapper._new_asset_ptr(exchange.asset_counter)

    def __del__(self):
        Wrapper._free_asset_ptr(self.ptr)

    def load_from_csv(self, file_name : str):
        self.file_name = c_char_p(file_name.encode("utf-8"))
        Wrapper._asset_from_csv(self.ptr, self.file_name)
        
    def load_from_df(self, df : pd.DataFrame):
        values = df.values.flatten().astype(np.float32)
        epoch_index = df.index.values.astype(np.float32)
        
        values_p = values.ctypes.data_as(POINTER(c_float))
        epoch_index_p = epoch_index.ctypes.data_as(POINTER(c_float))
        
        Wrapper._asset_from_pointer(
            self.ptr,
            epoch_index_p,
            values_p,
            df.shape[0],
            df.shape[1]
        )
        
        columns = df.columns
        for index, column in enumerate(columns):
            Wrapper._register_header(
                self.ptr, 
                c_char_p(column.encode("utf-8")),
                index
            )
        
        
    def set_format(self, digit_format : str, open_col : int, close_col : int):
        Wrapper._set_asset_format(
            self.ptr,
            c_char_p(digit_format.encode("utf-8")),
            open_col,
            close_col
        )

    def rows(self):
        return Wrapper._rows(self.ptr)
    
    def columns(self):
        return Wrapper._columns(self.ptr)

    def index(self):
        index_ptr = Wrapper._get_asset_index(self.ptr)
        return np.ctypeslib.as_array(index_ptr, shape=(self.rows(),))

    def data(self):
        data_ptr = Wrapper._get_asset_data(self.ptr)
        asset_data = np.ctypeslib.as_array(data_ptr, shape=(self.rows()*self.columns(),))
        return np.reshape(asset_data,(-1,self.columns()))

    @staticmethod
    def _data(ptr):
        M = Wrapper._columns(ptr)
        N = Wrapper._rows(ptr)
        data_ptr = Wrapper._get_asset_data(ptr)
        asset_data = np.ctypeslib.as_array(data_ptr, shape=(
            M*N,))
        return np.reshape(asset_data,(-1,M))

    def df(self):
        asset_index = self.index()
        asset_data = self.data()
        return pd.DataFrame(index = asset_index, data = asset_data)
    
if __name__ == "__main__":
    pass