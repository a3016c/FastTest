import sys
from ctypes import *
import numpy as np
from enum import Enum
import Wrapper
from Exchange import Exchange, Asset
from Order import OrderState

class Broker():
    def __init__(self, exchange : Exchange, logging = True, margin = False, debug = False) -> None:
        self.exchange_map = {exchange.exchange_name : exchange} 
        self.id = None
        self.logging = logging 
        self.debug = debug
        self.margin = margin
        self.ptr = Wrapper._new_broker_ptr(exchange.ptr, logging, margin, debug)

    def __del__(self):
        Wrapper._free_broker_ptr(self.ptr)
        
    def build(self):
        Wrapper._build_broker(self.ptr)
        
    def register_exchange(self, exchange : Exchange):
        if(exchange.exchange_id == None):
            raise Exception("broker not registered to FastTest")
        self.exchange_map[exchange.exchange_name] = exchange
        Wrapper._broker_register_exchange(self.ptr, exchange.ptr)
        
    def get_order_count(self):
        return Wrapper._get_order_count(self.ptr)
        
    def get_total_position_count(self):
        return Wrapper._get_position_count(self.ptr)
    
    def get_open_position_count(self):
        return Wrapper._get_open_position_count(self.ptr)
    
    def position_exists(self, asset_name):
        asset_id = self.exchange.asset_map[asset_name]
        return Wrapper._position_exists(self.ptr, asset_id)
    
    def get_nlv(self):
        return Wrapper._get_nlv(self.ptr)
    
    def get_cash(self):
        return Wrapper._get_cash(self.ptr)
    
    def get_positions(self):
        position_count = self.get_open_position_count()
        open_positions = Wrapper.PositionArrayStruct(position_count)
        position_struct_pointer = pointer(open_positions)
        Wrapper._get_positions(self.ptr, position_struct_pointer)
        
        return open_positions
            
    def get_position(self, asset_name : str):
        asset_id = self.exchange.asset_map[asset_name]
        position_struct = Wrapper.PositionStruct()
        position_struct_pointer = pointer(position_struct)
        Wrapper._get_position(self.ptr, position_struct_pointer)
        return position_struct
          
    def get_position_ptr(self, asset_name : str):
        asset_id = self.exchange.asset_map[asset_name]
        return Wrapper._get_position_ptr(self.ptr, asset_id)
    
    def get_history_length(self):
        return Wrapper._broker_get_history_length(self.ptr)
    
    def get_cash_history(self):
        cash_ptr = Wrapper._broker_get_cash_history(self.ptr)
        return np.ctypeslib.as_array(cash_ptr, shape=(self.get_history_length(),))
    
    def get_nlv_history(self):
        cash_ptr = Wrapper._broker_get_nlv_history(self.ptr)
        return np.ctypeslib.as_array(cash_ptr, shape=(self.get_history_length(),))
    
    def get_margin_history(self):
        cash_ptr = Wrapper._broker_get_margin_history(self.ptr)
        return np.ctypeslib.as_array(cash_ptr, shape=(self.get_history_length(),))
        
    def get_order_history(self):
        order_count = self.get_order_count()
        order_history = Wrapper.OrderHistoryStruct(order_count)
        order_struct_pointer = pointer(order_history)
        Wrapper._get_order_history(self.ptr, order_struct_pointer)
        return order_history
    
    def get_position_history(self):
        position_count = self.get_total_position_count()
        position_history = Wrapper.PositionArrayStruct(position_count)
        order_struct_pointer = pointer(position_history)
        Wrapper._get_position_history(self.ptr, order_struct_pointer)
        return position_history

    def place_market_order(self, asset_name : str, units : float, cheat_on_close = False, exchange_name = "default", strategy_id = 0):
        exchange = self.exchange_map[exchange_name]
        exchange_id = exchange.exchange_id
        asset_id = exchange.asset_map[asset_name]
        
        return OrderState(Wrapper._place_market_order(
            self.ptr,
            asset_id,
            units,
            cheat_on_close,
            exchange_id,
            strategy_id
            )
        )
        
    def place_limit_order(self, asset_name : str, units : float, limit : float, cheat_on_close = False, exchange_name = "default", strategy_id = 0):
        exchange = self.exchange_map[exchange_name]
        exchange_id = exchange.exchange_id
        asset_id = exchange.asset_map[asset_name]

        return OrderState(Wrapper._place_limit_order(
            self.ptr,
            asset_id,
            units,
            limit,
            cheat_on_close,
            exchange_id,
            strategy_id
            )
        )
        
    def place_stoploss_order(self, units : float, stop_loss : float, asset_name = None, order_id = None, cheat_on_close = False, exchange_name = "default", strategy_id = 0):

        if asset_name != None:
            
            exchange = self.exchange_map[exchange_name]
            exchange_id = exchange.exchange_id
            asset_id = exchange.asset_map[asset_name]
            position_ptr = Wrapper._get_position_ptr(self.ptr, asset_id)
            
            return OrderState(Wrapper._position_place_stoploss_order(
                self.ptr,
                position_ptr,
                units,
                stop_loss,
                cheat_on_close
                )
            )
        elif order_id != None:
            return OrderState(Wrapper._order_place_stoploss_order(
                self.ptr,
                order_id,
                units,
                stop_loss,
                cheat_on_close
                )
            )
        
    def reset(self):
        Wrapper._reset_broker(self.ptr)