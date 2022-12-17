import sys
from ctypes import *
from Asset import Asset

lib_path = r"C:\Users\bktor\Desktop\C++\FastTestLib\Debug\FASTTESTLIB.dll"
try:
    FastTest = CDLL(lib_path)
except OSError:
    print("Unable to load the system C library")
    sys.exit()

"""Exchange wrapper"""
_new_exchange_ptr = FastTest.CreateExchangePtr
_new_exchange_ptr.restype = c_void_p
"""====================================="""
_free_exchange_ptr = FastTest.DeleteExchangePtr
_free_exchange_ptr.argtypes = [c_void_p]
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
"""====================================="""
_get_market_price = FastTest.get_market_price
_get_market_price.argtypes = [c_void_p,c_char_p,c_bool]
_get_market_price.restype = c_float
"""====================================="""
_get_market_view = FastTest.get_market_view
_get_market_view.argtypes = [c_void_p]
"""====================================="""
_reset_exchange = FastTest.reset_exchange
_reset_exchange.argtypes = [c_void_p]

class Exchange():
    def __init__(self) -> None:
        self.ptr = _new_exchange_ptr()

    def __del__(self):
        _free_exchange_ptr(self.ptr)

    def reset(self):
        _reset_exchange(self.ptr)

    def register_asset(self, asset : Asset):
        _register_asset(asset.ptr, self.ptr)

    def asset_count(self):
        return _asset_count(self.ptr)

    def build(self):
        _build_exchange(self.ptr)

    def get_market_price(self, asset_name : str, on_close = True):
        return _get_market_price(
            self.ptr, 
            c_char_p(asset_name.encode("utf-8")),
            c_bool(on_close)
        )

    def get_market_view(self):
        _get_market_view(self.ptr)