import sys
from ctypes import *
import numpy as np
from Asset import Asset
from enum import Enum
import LibWrapper

class OrderState(Enum):
	ACCEPETED = 0
	OPEN = 1
	FILLED = 2
	CANCELED = 3
	BROKER_REJECTED = 4

class Broker():
    def __init__(self, exchange_ptr : c_void_p, logging = True) -> None:

        self.ptr = LibWrapper._new_broker_ptr(exchange_ptr, logging)

    def __del__(self):
        LibWrapper._free_broker_ptr(self.ptr)

    def get_order_count(self):
        return LibWrapper._get_order_count(self.ptr)

    def place_market_order(self, asset_name : str, units : float, cheat_on_close = False):
        return OrderState(LibWrapper._place_market_order(
            self.ptr,
            c_char_p(asset_name.encode("utf-8")),
            units,
            cheat_on_close
            )
        )
    def place_limit_order(self, asset_name : str, units : float, limit : float, cheat_on_close = False):
        return OrderState(LibWrapper._place_limit_order(
            self.ptr,
            c_char_p(asset_name.encode("utf-8")),
            units,
            limit,
            cheat_on_close
            )
        )

    def get_order_history(self):
        order_history_ptr = LibWrapper._get_order_history(self.ptr)
        asset_data = np.ctypeslib.as_array(order_history_ptr, shape=(self.get_order_count(),))

    def reset(self):
        LibWrapper._reset_broker(self.ptr)