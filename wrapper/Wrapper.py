import time
from ctypes import *
from numpy.ctypeslib import ndpointer
import sys

lib_path = r"/Users/nathantormaschy/Desktop/C++/FastTest/build/build/libFastTest.dylib"

FastTest = cdll.LoadLibrary(lib_path)

class OrderStruct(Structure):
    _fields_ = [
        ('order_type',c_uint),
        ('order_state',c_uint),
        ('units',c_float),
        ('fill_price',c_float),
        ('order_id',c_uint),
        ('asset_id',c_uint),
        ('order_create_time',c_long),
        ('order_fill_time',c_long)
    ]
    
class OrderHistoryStruct(Structure):
    _fields_ = [
        ('number_orders',c_uint),
        ('ORDER_ARRAY',POINTER(POINTER(OrderStruct)))
    ]
    def __init__(self,number_orders):
        elements = (POINTER(OrderStruct)*number_orders)()
        self.ORDER_ARRAY = cast(elements,POINTER(POINTER(OrderStruct)))
        self.number_orders = number_orders

        for num in range(0,number_orders):
            self.ORDER_ARRAY[num] = pointer(OrderStruct())
            
    def __len__(self):
        return self.number_orders
    
class PositionStruct(Structure):
    _fields_ = [
        ('average_price', c_float),
        ('close_price', c_float),
        ('units',c_float),
        ('position_id',c_uint),
        ('asset_id',c_uint),
        ('position_create_time',c_long),
        ('position_close_time',c_long),
        ('realized_pl', c_float),
        ('unrealized_pl', c_float)
    ]

class PositionHistoryStruct(Structure):
    _fields_ = [
        ('number_positions',c_uint),
        ('POSITION_ARRAY',POINTER(POINTER(PositionStruct)))
    ]
    def __init__(self,number_positions):
        elements = (POINTER(PositionStruct)*number_positions)()
        self.POSITION_ARRAY = cast(elements,POINTER(POINTER(PositionStruct)))
        self.number_positions = number_positions

        for num in range(0,number_positions):
            self.POSITION_ARRAY[num] = pointer(PositionStruct())
            
    def __len__(self):
        return self.number_positions

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

_fastTest_reset = FastTest.reset_fastTest
_fastTest_reset.argtypes = [c_void_p]

_rows = FastTest.rows
_rows.argtypes = [c_void_p]
_rows.restype = c_size_t

"""ASSET WRAPPER"""
_rows = FastTest.rows
_rows.argtypes = [c_void_p]
_rows.restype = c_size_t

_new_asset_ptr = FastTest.CreateAssetPtr
_new_asset_ptr.argtypes = [c_uint]
_new_asset_ptr.restype = c_void_p

_free_asset_ptr = FastTest.DeleteAssetPtr
_free_asset_ptr.argtypes = [c_void_p]

_asset_from_csv = FastTest.load_from_csv 
_asset_from_csv.argtypes = [c_void_p,c_char_p]

_asset_from_pointer = FastTest.load_from_pointer
_asset_from_pointer.argtypes = [c_void_p, POINTER(c_float), POINTER(c_float), c_size_t, c_size_t]

_register_header = FastTest.register_header
_register_header.argtypes = [c_void_p, c_char_p, c_uint]

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

_get_position_count = FastTest.get_position_count
_get_position_count.argtypes = [c_void_p]
_get_position_count.restype = c_int

_position_exists = FastTest.position_exists
_position_exists.argtypes = [c_void_p, c_uint]
_position_exists.restype = c_bool

_get_order_history = FastTest.get_order_history
_get_order_history.argtypes = [c_void_p,POINTER(OrderHistoryStruct)]

_get_position_history = FastTest.get_position_history
_get_position_history.argtypes = [c_void_p,POINTER(PositionHistoryStruct)]

_place_market_order = FastTest.place_market_order
_place_market_order.argtypes = [c_void_p, c_uint, c_float, c_bool]
_place_market_order.restype = c_uint

_place_limit_order = FastTest.place_limit_order
_place_limit_order.argtypes = [c_void_p, c_uint, c_float, c_float, c_bool]
_place_limit_order.restype = c_uint

_get_position_ptr = FastTest.get_position_ptr
_get_position_ptr.argtypes = [c_void_p, c_uint]
_get_position_ptr.restype = c_void_p

_get_positions = FastTest.get_positions
_get_positions.argtypes = [c_void_p,POINTER(PositionHistoryStruct)]

_position_place_stoploss_order = FastTest.position_add_stoploss
_position_place_stoploss_order.argtypes = [c_void_p, c_void_p, c_float, c_float, c_bool]
_position_place_stoploss_order.restype = c_uint


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
_get_market_price.argtypes = [c_void_p,c_uint,c_bool]
_get_market_price.restype = c_float

_get_market_feature = FastTest.get_market_feature
_get_market_feature.argtypes = [c_void_p,c_uint,c_char_p]
_get_market_feature.restype = c_float

_get_market_view = FastTest.get_market_view
_get_market_view.argtypes = [c_void_p]

_reset_exchange = FastTest.reset_exchange
_reset_exchange.argtypes = [c_void_p]

_asset_count = FastTest.asset_count
_asset_count.argtypes = [c_void_p]
_asset_count.restype = c_int

_get_asset_ptr = FastTest.get_asset_ptr
_get_asset_ptr.argtypes = [c_void_p, c_uint]  
_get_asset_ptr.restype = c_void_p