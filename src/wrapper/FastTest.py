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
new_asset_ptr = FastTest.CreateAssetPtr
new_asset_ptr.restype = c_void_p
"""====================================="""
free_asset_ptr = FastTest.DeleteAssetPtr
free_asset_ptr.argtypes = [c_void_p]
"""====================================="""
asset_from_csv = FastTest.load_from_csv 
asset_from_csv.argtypes = [c_void_p,c_char_p]
"""====================================="""
set_asset_format = FastTest.set_format 
set_asset_format.argtypes = [c_void_p,c_char_p, c_size_t, c_size_t]

"""Exchange wrapper"""
new_exchange_ptr = FastTest.CreateExchangePtr
new_exchange_ptr.restype = c_void_p
"""====================================="""
free_exchange_ptr = FastTest.DeleteExchangePtr
free_exchange_ptr.argtypes = [c_void_p]
"""====================================="""
_build_exchange = FastTest.build_exchange
_build_exchange.argtypes = [c_void_p]
"""====================================="""
_register_asset = FastTest.register_asset 
_register_asset.argtypes = [c_void_p,c_void_p]
"""====================================="""
_asset_count = FastTest.asset_count
_asset_count.argtypes = [c_void_p]
_asset_count.restype = c_int

rows = FastTest.rows
rows.argtypes = [c_void_p]
rows.restype = c_size_t
columns = FastTest.columns
columns.argtypes = [c_void_p]
columns.restype = c_size_t

class Asset():
    def __init__(self) -> None:
        self.ptr = new_asset_ptr()
    
    def __del__(self):
        free_asset_ptr(self.ptr)

    def load_from_csv(self, file_name : str):
        self.file_name = c_char_p(file_name)
        asset_from_csv(self.ptr, self.file_name)

    def set_format(self, digit_format : str, open_col : int, close_col : int):
        set_asset_format(
            self.ptr,
            c_char_p(digit_format.encode("utf-8")),
            open_col,
            close_col
        )

    def rows(self):
        return rows(self.ptr)
    
    def columns(self):
        return columns(self.ptr)

class Exchange():
    def __init__(self) -> None:
        self.ptr = new_exchange_ptr()

    def __del__(self):
        free_exchange_ptr(self.ptr)

    def register_asset(self, asset : Asset):
        _register_asset(asset.ptr, self.ptr)

    def asset_count(self):
        return _asset_count(self.ptr)

    def build(self):
        _build_exchange(self.ptr)


file_name = b"C:/Users/bktor/Desktop/Python/FastTest/tests/data/test2.csv"
new_asset = Asset()
new_asset.set_format("%d-%d-%d", 0, 1)
new_asset.load_from_csv(file_name)
print(new_asset.rows())

exchange = Exchange()
exchange.register_asset(new_asset)
exchange.build()