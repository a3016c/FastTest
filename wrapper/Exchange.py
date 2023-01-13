import sys
from ctypes import *
import Wrapper
import numpy as np
import pandas as pd

global g_asset_counter 
g_asset_counter = 0

class Exchange():
    def __init__(self, logging = False, exchange_name = "default") -> None:
        self.exchange_name = exchange_name
        self.exchange_id = None
        self.ptr = Wrapper._new_exchange_ptr(logging)
        self.asset_map = {}
        self.id_map = {}
        self.asset_counter = 0

    def __del__(self):
        Wrapper._free_exchange_ptr(self.ptr)

    def reset(self):
        Wrapper._reset_exchange(self.ptr)

    def register_asset(self, asset):
        self.asset_map[asset.asset_name] = asset.asset_id
        self.id_map[asset.asset_id] = asset.asset_name
        self.asset_counter += 1
        Wrapper._register_asset(asset.ptr, self.ptr)

    def build(self):
        Wrapper._build_exchange(self.ptr)
        
    def get_exchange_index_length(self):
        return Wrapper._get_exchange_index_length(self.ptr)
        
    def get_datetime_index(self):
        index_ptr = Wrapper._get_exchange_datetime_index(self.ptr)
        length = self.get_exchange_index_length()
        return np.ctypeslib.as_array(index_ptr, shape=(length,))

    def get_market_price(self, asset_name : str, on_close = True):
        asset_id = self.asset_map[asset_name]
        return Wrapper._get_market_price(
            self.ptr, 
            asset_id,
            c_bool(on_close)
        )
        
    def get(self, asset_name : str, column : str, index = 0):
        asset_id = self.asset_map[asset_name]
        return Wrapper._get_market_feature(
            self.ptr, 
            asset_id,
            c_char_p(column.encode("utf-8")),
            index
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
        global g_asset_counter
        self.asset_id = g_asset_counter
        g_asset_counter += 1
        self.ptr = Wrapper._new_asset_ptr(self.asset_id, exchange.exchange_id)

    def __del__(self):
        Wrapper._free_asset_ptr(self.ptr)

    def load_from_csv(self, file_name : str):
        self.file_name = c_char_p(file_name.encode("utf-8"))
        Wrapper._asset_from_csv(self.ptr, self.file_name)
        self.headers = pd.read_csv(file_name, index_col=0, nrows=0).columns.tolist()
        
    def load_from_df(self, df : pd.DataFrame, nano = False):
        values = df.values.flatten().astype(np.float32)
        epoch_index = df.index.values.astype(np.float32)
        if nano: epoch_index /=  1e9
        
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
        self.headers = columns
                    
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
    
    def df(self):
        asset_index = self.index()
        asset_data = self.data()
        return pd.DataFrame(index = asset_index, data = asset_data, columns = self.headers)
    
    @staticmethod
    def _index(ptr):
        index_ptr = Wrapper._get_asset_index(ptr)
        rows = Wrapper._rows(ptr)
        return np.ctypeslib.as_array(index_ptr, shape=(rows,))
        
    @staticmethod
    def _data(ptr):
        M = Wrapper._columns(ptr)
        N = Wrapper._rows(ptr)
        data_ptr = Wrapper._get_asset_data(ptr)
        asset_data = np.ctypeslib.as_array(data_ptr, shape=(
            M*N,))
        return np.reshape(asset_data,(-1,M))

if __name__ == "__main__":
    pass