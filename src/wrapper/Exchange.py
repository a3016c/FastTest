import sys
from ctypes import *
from Asset import Asset

class Exchange():
    def __init__(self, lib_path, logging = False) -> None:
        try:
            FastTest = CDLL(lib_path)
        except OSError:
            print("Unable to load the system C library")
            sys.exit()

        """Exchange wrapper"""
        self._new_exchange_ptr = FastTest.CreateExchangePtr
        self._new_exchange_ptr.argtypes = [c_bool]
        self._new_exchange_ptr.restype = c_void_p
        """====================================="""
        self._free_exchange_ptr = FastTest.DeleteExchangePtr
        self._free_exchange_ptr.argtypes = [c_void_p]
        """====================================="""
        self._build_exchange = FastTest.build_exchange
        self._build_exchange.argtypes = [c_void_p]
        """====================================="""
        self._register_asset = FastTest.register_asset 
        self._register_asset.argtypes = [c_void_p,c_void_p]
        """====================================="""
        self._asset_count = FastTest.asset_count
        self._asset_count.argtypes = [c_void_p]
        self._asset_count.restype = c_int
        """====================================="""
        self._get_market_price = FastTest.get_market_price
        self._get_market_price.argtypes = [c_void_p,c_char_p,c_bool]
        self._get_market_price.restype = c_float
        """====================================="""
        self._get_market_view = FastTest.get_market_view
        self._get_market_view.argtypes = [c_void_p]
        """====================================="""
        self._reset_exchange = FastTest.reset_exchange
        self._reset_exchange.argtypes = [c_void_p]
        self.ptr = self._new_exchange_ptr(logging)

    def __del__(self):
        self._free_exchange_ptr(self.ptr)

    def reset(self):
        self._reset_exchange(self.ptr)

    def register_asset(self, asset : Asset):
        self._register_asset(asset.ptr, self.ptr)

    def asset_count(self):
        return self._asset_count(self.ptr)

    def build(self):
        self._build_exchange(self.ptr)

    def get_market_price(self, asset_name : str, on_close = True):
        return self._get_market_price(
            self.ptr, 
            c_char_p(asset_name.encode("utf-8")),
            c_bool(on_close)
        )

    def get_market_view(self):
        self._get_market_view(self.ptr)