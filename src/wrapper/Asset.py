import ctypes
import os
import sys
import numpy as np
import pandas as pd
from ctypes import *
import time 
import LibWrapper


class Asset():
    def __init__(self, asset_name : str) -> None:
        self.asset_name = asset_name
        self.ptr = LibWrapper._new_asset_ptr(c_char_p(asset_name.encode("utf-8")))

    def __del__(self):
        LibWrapper._free_asset_ptr(self.ptr)

    def load_from_csv(self, file_name : str):
        self.file_name = c_char_p(file_name.encode("utf-8"))
        LibWrapper._asset_from_csv(self.ptr, self.file_name)

    def set_format(self, digit_format : str, open_col : int, close_col : int):
        LibWrapper._set_asset_format(
            self.ptr,
            c_char_p(digit_format.encode("utf-8")),
            open_col,
            close_col
        )

    def rows(self):
        return LibWrapper._rows(self.ptr)
    
    def columns(self):
        return LibWrapper._columns(self.ptr)

    def index(self):
        index_ptr = LibWrapper._get_asset_index(self.ptr)
        return np.ctypeslib.as_array(index_ptr, shape=(self.rows(),))

    def data(self):
        data_ptr = LibWrapper._get_asset_data(self.ptr)
        asset_data = np.ctypeslib.as_array(data_ptr, shape=(self.rows()*self.columns(),))
        return np.reshape(asset_data,(-1,self.columns()))

    @staticmethod
    def _data(ptr):
        M = LibWrapper._columns(ptr)
        N = LibWrapper._rows(ptr)
        data_ptr = LibWrapper._get_asset_data(ptr)
        asset_data = np.ctypeslib.as_array(data_ptr, shape=(
            M*N,))
        return np.reshape(asset_data,(-1,M))

    def df(self):
        asset_index = self.index()
        asset_data = self.data()
        return pd.DataFrame(index = asset_index, data = asset_data)
