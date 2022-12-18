from enum import Enum
from ctypes import *
import LibWrapper

class OrderType(Enum):
	MARKET_ORDER = 0
	LIMIT_ORDER = 1
	STOP_LOSS_ORDER = 2
	TAKE_PROFIT_ORDER = 3

class OrderSchedule():
    def __init__(self, **kwargs) -> None:
        self.order_type = kwargs["order_type"]
        self.asset_name = kwargs["asset_name"]
        self.i = kwargs["i"]
        self.units = kwargs["units"]
        self.limit = kwargs.get("limit")
        self.cheat_on_close = kwargs.get("cheat_on_close")

class Order():
    def __init__(self, order_ptr : c_void_p) -> None:
        self.ptr = order_ptr
    
    def order_type(self):
        return LibWrapper._order_type(self.ptr)