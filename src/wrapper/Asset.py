import ctypes
import os
import sys
from ctypes import *
import time 

class Asset():
    def __init__(self, lib_path : str, asset_name : str) -> None:
        try:
            FastTest = CDLL(lib_path)
        except OSError:
            print("Unable to load the system C library")
            sys.exit()
        """Asset wrapper"""
        self._new_asset_ptr = FastTest.CreateAssetPtr
        self._new_asset_ptr.argtypes = [c_char_p]
        self._new_asset_ptr.restype = c_void_p

        self.ptr = self._new_asset_ptr(c_char_p(asset_name.encode("utf-8")))
        self.asset_name = asset_name

        """====================================="""
        self._free_asset_ptr = FastTest.DeleteAssetPtr
        self._free_asset_ptr.argtypes = [c_void_p]
        """====================================="""
        self._asset_from_csv = FastTest.load_from_csv 
        self._asset_from_csv.argtypes = [c_void_p,c_char_p]
        """====================================="""
        self._set_asset_format = FastTest.set_format 
        self._set_asset_format.argtypes = [c_void_p,c_char_p, c_size_t, c_size_t]
        """====================================="""
        self._rows = FastTest.rows
        self._rows.argtypes = [c_void_p]
        self._rows.restype = c_size_t
        """====================================="""
        self._columns = FastTest.columns
        self._columns.argtypes = [c_void_p]
        self._columns.restype = c_size_t

    def __del__(self):
        self._free_asset_ptr(self.ptr)

    def load_from_csv(self, file_name : str):
        self.file_name = c_char_p(file_name)
        self._asset_from_csv(self.ptr, self.file_name)

    def set_format(self, digit_format : str, open_col : int, close_col : int):
        self._set_asset_format(
            self.ptr,
            c_char_p(digit_format.encode("utf-8")),
            open_col,
            close_col
        )

    def rows(self):
        return self._rows(self.ptr)
    
    def columns(self):
        return self._columns(self.ptr)
