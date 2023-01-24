import sys
from ctypes import *
from enum import Enum
import os
import sys

import numpy as np

SCRIPT_DIR = os.path.dirname(__file__)
sys.path.append(os.path.dirname(SCRIPT_DIR))

from wrapper import Wrapper
from wrapper.Exchange import Exchange, Asset
from wrapper.Order import OrderState

class Broker():
    def __init__(self, exchange : Exchange, cash = 100000, logging = True, margin = False, debug = False) -> None:
        self.exchange_map = {exchange.exchange_name : exchange} 
        self.id = None
        self.logging = logging 
        self.debug = debug
        self.margin = margin
        self.ptr = Wrapper._new_broker_ptr(exchange.ptr, cash, logging, margin, debug)

    def __del__(self):
        Wrapper._free_broker_ptr(self.ptr)
        
    def build(self):
        Wrapper._build_broker(self.ptr)
        
    def register_exchange(self, exchange : Exchange):
        if(not exchange.is_registered()):
            raise Exception("Exchange is not yet registered to the FastTest")
        
        self.exchange_map[exchange.exchange_name] = exchange
        Wrapper._broker_register_exchange(self.ptr, exchange.ptr)
        
    def get_order_count(self):
        return Wrapper._get_order_count(self.ptr)
        
    def get_total_position_count(self):
        return Wrapper._get_position_count(self.ptr)
    
    def get_open_position_count(self):
        return Wrapper._get_open_position_count(self.ptr)
    
    def position_exists(self, asset_name,
                        exchange_name = "default",
                        account_id = 0):
        exchange = self.exchange_map[exchange_name]
        asset_id = exchange.asset_map[asset_name]
        return Wrapper._position_exists(self.ptr, asset_id, account_id)
    
    def get_nlv(self, account_id = -1):
        return Wrapper._get_nlv(self.ptr, account_id)
    
    def get_cash(self, account_id = -1):
        """_summary_

        Args:
            account_id (int, optional): account id of the account to get cash, -1 for all accounts combined

        Returns:
            float: amount of cash available in a given account
        """
        return Wrapper._get_cash(self.ptr, account_id)
    
    def get_positions(self, account_id = 0):
        """_summary_

        Args:
            account_id (int, optional): the account id of the account to retrieve the positions of

        Returns:
            PositionArrayStruct: an array of PositionStructs
        """
        position_count = self.get_open_position_count()
        open_positions = Wrapper.PositionArrayStruct(position_count)
        position_struct_pointer = pointer(open_positions)
        Wrapper._get_positions(self.ptr, position_struct_pointer, account_id)
        
        return open_positions
            
    def get_position(self, asset_name : str,
                     exchange_name = "default",
                     account_id = 0):
        """_summary_

        Args:
            asset_name (str): the asset name of the position to get
            exchange_name (str, optional): the exchange name that the asset is listed on
            account_id (int, optional): the id of the account that the position is in

        Returns:
            PositionStruct: position struct the requested position
        """
        exchange = self.exchange_map[exchange_name]
        asset_id = exchange.asset_map[asset_name]
        position_struct = Wrapper.PositionStruct()
        position_struct_pointer = pointer(position_struct)
        Wrapper._get_position(self.ptr, asset_id, position_struct_pointer, account_id)
        return position_struct
          
    def get_position_ptr(self, asset_name : str, account_id = 0):
        """_summary_

        Args:
            asset_name (str): the asset name of the position pointer to get
            account_id (int, optional): the id of the account containing the position

        Returns:
            c_void+_ptr : a pointer to a C++ position object
        """
        asset_id = self.exchange.asset_map[asset_name]
        return Wrapper._get_position_ptr(self.ptr, asset_id, account_id)
    
    def get_history_length(self):
        """_summary_

        Returns:
            int: the length of the nlv_history of the broker (how many valuations of the portfolio there were)
        """
        return Wrapper._broker_get_history_length(self.ptr)
    
    def get_cash_history(self):
        """_summary_

        Returns:
            numpy array: an array of floats representing available cash at every time period 
        """
        cash_ptr = Wrapper._broker_get_cash_history(self.ptr)
        return np.ctypeslib.as_array(cash_ptr, shape=(self.get_history_length(),))
    
    def get_nlv_history(self):
        """_summary_

        Returns:
            numpy array: an array of floats representing net liquidation value at every time period 
        """
        nlv_ptr = Wrapper._broker_get_nlv_history(self.ptr)
        return np.ctypeslib.as_array(nlv_ptr, shape=(self.get_history_length(),))
    
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
        position_struct_pointer = pointer(position_history)
        Wrapper._get_position_history(self.ptr, position_struct_pointer)
        return position_history

    def place_market_order(self, asset_name : str, units : float, 
                           stop_loss_on_fill = 0,
                           stop_loss_limit_pct = False,
                           cheat_on_close = False, 
                           exchange_name = "default",
                           strategy_id = 0,
                           account_id = 0):
        """_summary_

        Args:
            asset_name (str): name of the asset to place the order for
            units (float): how many units to buy/sell
            stop_loss_on_fill (float, optional): stop loss level of stop loss placed on fill. Defaults to 0.
            stop_loss_limit_pct (bool, optional): is the stop loss level a percentage of the current price. Defaults to False.
            cheat_on_close (bool, optional): = allow position to be execute at end of current candle. Defaults to False.
            exchange_name (str, optional): name of the exchange to place the order to. Defaults to "default".
            strategy_id (int, optional): id of the strategy placing the trade. Defaults to 0.
            account_id (int, optional): id of the account the order was placed for. Defaults to 0.

        Returns:
            OrderResponse: brokers response to the order containing the order id and state
        """
        
        exchange = self.exchange_map[exchange_name]
        exchange_id = exchange.exchange_id
        asset_id = exchange.asset_map[asset_name]
        
        order_response = Wrapper.OrderResponse()
        order_response_pointer = pointer(order_response)
        Wrapper._place_market_order(
            self.ptr,
            order_response_pointer,
            asset_id,
            units,
            cheat_on_close,
            exchange_id,
            strategy_id,
            account_id
            )
        
        if(stop_loss_on_fill > 0):
            self.place_stoploss_order(
                units = -1*units,
                order_id = order_response.order_id,
                stop_loss = stop_loss_on_fill,
                limit_pct = stop_loss_limit_pct,
                account_id = account_id
            )
        
        return order_response
        
    def place_limit_order(self, asset_name : str, units : float, limit : float,
                        stop_loss_on_fill = 0,
                        stop_loss_limit_pct = False,
                        cheat_on_close = False,
                        exchange_name = "default",
                        strategy_id = 0,
                        account_id = 0):
        
        exchange = self.exchange_map[exchange_name]
        exchange_id = exchange.exchange_id
        asset_id = exchange.asset_map[asset_name]

        order_response = Wrapper.OrderResponse()
        order_response_pointer = pointer(order_response)
        Wrapper._place_limit_order(
            self.ptr,
            order_response_pointer,
            asset_id,
            units,
            limit,
            cheat_on_close,
            exchange_id,
            strategy_id,
            account_id
            )
        
        if(stop_loss_on_fill > 0):
            self.place_stoploss_order(
                units = -1*units,
                order_id = order_response.order_id,
                stop_loss = stop_loss_on_fill,
                limit_pct = stop_loss_limit_pct,
                account_id = account_id
            )
            
        return order_response
        
    def place_stoploss_order(self, units : float, stop_loss : float, 
                             limit_pct = False,
                             asset_name = None,
                             order_id = None,
                             cheat_on_close = False,
                             exchange_name = "default",
                             strategy_id = 0,
                             account_id = 0):
        
        exchange = self.exchange_map[exchange_name]
        exchange_id = exchange.exchange_id

        order_response = Wrapper.OrderResponse()
        order_response_pointer = pointer(order_response)
        
        if asset_name != None:
            asset_id = exchange.asset_map[asset_name]
            position_ptr = Wrapper._get_position_ptr(self.ptr, asset_id,account_id)
            
            Wrapper._position_place_stoploss_order(
                self.ptr,
                order_response_pointer,
                position_ptr,
                units,
                stop_loss,
                cheat_on_close,
                exchange_id,
                limit_pct
                )
    
        elif order_id != None:
            Wrapper._order_place_stoploss_order(
                self.ptr,
                order_response_pointer,
                order_id,
                units,
                stop_loss,
                cheat_on_close,
                exchange_id,
                limit_pct
                )
            
        else:
            raise Exception("Must pass in order id or asset name")

        return order_response
        
    def reset(self):
        Wrapper._reset_broker(self.ptr)