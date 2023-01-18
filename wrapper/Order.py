from enum import Enum
import ctypes
import Wrapper

class OrderState(Enum):
	ACCEPETED = 0
	OPEN = 1
	FILLED = 2
	CANCELED = 3
	BROKER_REJECTED = 4

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
        self.cheat_on_close = kwargs.get("cheat_on_close") if kwargs.get("cheat_on_close") != None else False
        
        self.stop_loss_on_fill = kwargs.get("stop_loss_on_fill")
        if self.stop_loss_on_fill == None: self.stop_loss_on_fill = 0
        self.stop_loss_limit_pct = kwargs.get("stop_loss_limit_pct")
        if self.stop_loss_limit_pct == None: self.stop_loss_limit_pct = 0
        
        
        if kwargs.get("exchange_name") == None:
            self.exchange_name = "default"
        else:
            self.exchange_name = kwargs.get("exchange_name")
            
class Order():
    def __init__(self, order_ptr : ctypes.c_void_p) -> None:
        self.ptr = order_ptr
    
    def order_type(self):
        return Wrapper._order_type(self.ptr)