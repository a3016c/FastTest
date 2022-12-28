import sys
from ctypes import *
import numpy as np
from enum import Enum
import Wrapper
from Exchange import Exchange, Asset
from Order import OrderState

class Broker():
    def __init__(self, exchange : Exchange, logging = True) -> None:
        self.exchange = exchange 
        self.ptr = Wrapper._new_broker_ptr(exchange.ptr, logging)

    def __del__(self):
        Wrapper._free_broker_ptr(self.ptr)

    def get_order_count(self):
        return Wrapper._get_order_count(self.ptr)
    
    def get_total_position_count(self):
        return Wrapper._get_position_count(self.ptr)
    
    def position_exists(self, asset_name):
        asset_id = self.exchange.asset_map[asset_name]
        return Wrapper._position_exists(self.ptr, asset_id)
    
    def get_position_ptr(self, asset_name : str):
        asset_id = self.exchange.asset_map[asset_name]
        return Wrapper._get_position_ptr(self.ptr, asset_id)

    def get_order_history(self):
        order_count = self.get_order_count()
        order_history = Wrapper.OrderHistoryStruct(order_count)
        order_struct_pointer = pointer(order_history)
        Wrapper._get_order_history(self.ptr, order_struct_pointer)
        return order_history
    
    def get_position_history(self):
        position_count = self.get_total_position_count()
        position_history = Wrapper.PositionHistoryStruct(position_count)
        order_struct_pointer = pointer(position_history)
        Wrapper._get_position_history(self.ptr, order_struct_pointer)
        return position_history

    def place_market_order(self, asset_name : str, units : float, cheat_on_close = False):
        asset_id = self.exchange.asset_map[asset_name]
        return OrderState(Wrapper._place_market_order(
            self.ptr,
            asset_id,
            units,
            cheat_on_close
            )
        )
    def place_limit_order(self, asset_name : str, units : float, limit : float, cheat_on_close = False):
        asset_id = self.exchange.asset_map[asset_name]
        return OrderState(Wrapper._place_limit_order(
            self.ptr,
            asset_id,
            units,
            limit,
            cheat_on_close
            )
        )

    def reset(self):
        Wrapper._reset_broker(self.ptr)