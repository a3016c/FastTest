import time
from ctypes import *
from numpy.ctypeslib import ndpointer
import sys

lib_path = r"C:\Users\bktor\Desktop\C++\FastTestLib\x64\Release\FASTTESTLIB.dll"

try:
    FastTest = CDLL(lib_path)
except OSError:
    print("Unable to load the system C library")
    sys.exit()

"""FastTest wrapper"""
_new_fastTest_ptr = FastTest.CreateFastTestPtr
_new_fastTest_ptr.argtypes = [c_void_p, c_void_p, c_bool]
_new_fastTest_ptr.restype = c_void_p

_free_fastTest_ptr = FastTest.DeleteFastTestPtr
_free_fastTest_ptr.argtypes = [c_void_p]

_fastTest_forward_pass = FastTest.forward_pass
_fastTest_forward_pass.argtypes = [c_void_p]
_fastTest_forward_pass.restype = c_bool

_fastTest_backward_pass = FastTest.backward_pass
_fastTest_backward_pass.argtypes = [c_void_p]

_fastTest_reset = FastTest.reset_exchange
_fastTest_reset.argtypes = [c_void_p]

_rows = FastTest.rows
_rows.argtypes = [c_void_p]
_rows.restype = c_size_t

"""ASSET WRAPPER"""
_rows = FastTest.rows
_rows.argtypes = [c_void_p]
_rows.restype = c_size_t

_new_asset_ptr = FastTest.CreateAssetPtr
_new_asset_ptr.argtypes = [c_char_p]
_new_asset_ptr.restype = c_void_p

_free_asset_ptr = FastTest.DeleteAssetPtr
_free_asset_ptr.argtypes = [c_void_p]

_asset_from_csv = FastTest.load_from_csv 
_asset_from_csv.argtypes = [c_void_p,c_char_p]

_set_asset_format = FastTest.set_format 
_set_asset_format.argtypes = [c_void_p,c_char_p, c_size_t, c_size_t]

_columns = FastTest.columns
_columns.argtypes = [c_void_p]
_columns.restype = c_size_t

_get_asset_index = FastTest.get_asset_index
_get_asset_index.argtypes = [c_void_p]
_get_asset_index.restype = POINTER(c_float)

_get_asset_data = FastTest.get_asset_data
_get_asset_data.argtypes = [c_void_p]
_get_asset_data.restype = POINTER(c_float)

"""BROKER WRAPPER"""
_new_broker_ptr = FastTest.CreateBrokerPtr
_new_broker_ptr.argtypes =[c_void_p, c_bool]
_new_broker_ptr.restype = c_void_p

_free_broker_ptr = FastTest.CreateBrokerPtr
_free_broker_ptr.argtypes = [c_void_p]

_reset_broker = FastTest.reset_broker
_reset_broker.argtypes = [c_void_p]

_get_order_count = FastTest.get_order_count
_get_order_count.argtypes = [c_void_p]
_get_order_count.restype = c_int

_get_order_history = FastTest.get_order_history
_get_order_history.argtypes = [c_void_p]
_get_order_history.restype = c_void_p

_place_market_order = FastTest.place_market_order
_place_market_order.argtypes = [c_void_p, c_char_p, c_float, c_bool]
_place_market_order.restype = c_uint

_place_limit_order = FastTest.place_limit_order
_place_limit_order.argtypes = [c_void_p, c_char_p, c_float, c_float, c_bool]
_place_limit_order.restype = c_uint

"""ORDER WRAPPER"""
_order_type = FastTest.order_type
_order_type.argtypes = [c_void_p]
_order_type.restype = c_uint

"""Exchange wrapper"""
_new_exchange_ptr = FastTest.CreateExchangePtr
_new_exchange_ptr.argtypes = [c_bool]
_new_exchange_ptr.restype = c_void_p

_free_exchange_ptr = FastTest.DeleteExchangePtr
_free_exchange_ptr.argtypes = [c_void_p]

_build_exchange = FastTest.build_exchange
_build_exchange.argtypes = [c_void_p]

_register_asset = FastTest.register_asset 
_register_asset.argtypes = [c_void_p,c_void_p]

_get_market_price = FastTest.get_market_price
_get_market_price.argtypes = [c_void_p,c_char_p,c_bool]
_get_market_price.restype = c_float

_get_market_feature = FastTest.get_market_feature
_get_market_feature.argtypes = [c_void_p,c_char_p,c_char_p]
_get_market_feature.restype = c_float

_get_market_view = FastTest.get_market_view
_get_market_view.argtypes = [c_void_p]

_reset_exchange = FastTest.reset_exchange
_reset_exchange.argtypes = [c_void_p]

_asset_count = FastTest.asset_count
_asset_count.argtypes = [c_void_p]
_asset_count.restype = c_int

_get_asset_ptr = FastTest.get_asset_ptr
_get_asset_ptr.argtypes = [c_void_p, c_char_p]  
_get_asset_ptr.restype = c_void_p