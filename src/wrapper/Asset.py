import ctypes
import os
import sys
from ctypes import *
import time 

lib_path = r"C:\Users\bktor\Desktop\C++\FastTestLib\Debug\FASTTESTLIB.dll"
try:
    FastTest = CDLL(lib_path)
except OSError:
    print("Unable to load the system C library")
    sys.exit()

"""Asset wrapper"""
_new_asset_ptr = FastTest.CreateAssetPtr
_new_asset_ptr.argtypes = [c_char_p]
_new_asset_ptr.restype = c_void_p
"""====================================="""
_free_asset_ptr = FastTest.DeleteAssetPtr
_free_asset_ptr.argtypes = [c_void_p]
"""====================================="""
_asset_from_csv = FastTest.load_from_csv 
_asset_from_csv.argtypes = [c_void_p,c_char_p]
"""====================================="""
_set_asset_format = FastTest.set_format 
_set_asset_format.argtypes = [c_void_p,c_char_p, c_size_t, c_size_t]
"""====================================="""
rows = FastTest.rows
rows.argtypes = [c_void_p]
rows.restype = c_size_t
"""====================================="""
columns = FastTest.columns
columns.argtypes = [c_void_p]
columns.restype = c_size_t

class Asset():
    def __init__(self, asset_name : str) -> None:
        self.ptr = _new_asset_ptr(c_char_p(asset_name.encode("utf-8")))
        self.asset_name = asset_name
    
    def __del__(self):
        _free_asset_ptr(self.ptr)

    def load_from_csv(self, file_name : str):
        self.file_name = c_char_p(file_name)
        _asset_from_csv(self.ptr, self.file_name)

    def set_format(self, digit_format : str, open_col : int, close_col : int):
        _set_asset_format(
            self.ptr,
            c_char_p(digit_format.encode("utf-8")),
            open_col,
            close_col
        )

    def rows(self):
        return rows(self.ptr)
    
    def columns(self):
        return columns(self.ptr)
