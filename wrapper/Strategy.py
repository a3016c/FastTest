from ctypes import c_void_p
import sys 
import os

import pandas as pd
import numpy as np

import numba
from numba.core import types
from numba.experimental import jitclass

SCRIPT_DIR = os.path.dirname(__file__)
sys.path.append(os.path.dirname(SCRIPT_DIR))

from wrapper.Exchange import Exchange
from wrapper.Broker import Broker
from wrapper.Order import OrderSchedule
from wrapper import Wrapper
from wrapper.Wrapper import OrderType, OrderState

class Strategy():
    def __init__(self, broker : Broker, exchange : Exchange, strategy_name = "default") -> None:
        self.broker = broker 
        self.exchange = exchange
        self.strategy_name = strategy_name
        self.strategy_id = None
        
    def build(self):
        return

    def next(self):
        return 
                     
    def close_positions(self):
        positions = self.broker.get_positions()
        for i in range(positions.number_positions):
            position = positions.POSITION_ARRAY[i].contents
            asset_name = self.exchange.id_map[position.asset_id]
            self.broker.place_market_order(asset_name, -1*position.units)
            
class TestStrategy(Strategy):
    def __init__(self, order_schedule, broker = None, exchange = None, strategy_name = "default") -> None:
        super().__init__(broker,exchange,strategy_name)
        self.order_schedule = order_schedule
        self.i = 0
        
    def build(self):
        return

    def next(self):
        for order in self.order_schedule:
            if order.i == self.i:
                if order.order_type == OrderType.MARKET_ORDER:
                    res = self.broker.place_market_order(order.asset_name,order.units,
                                                        cheat_on_close = order.cheat_on_close,
                                                        stop_loss_on_fill= order.stop_loss_on_fill,
                                                        stop_loss_limit_pct = order.stop_loss_limit_pct,
                                                        exchange_name = order.exchange_name,
                                                        strategy_id = self.strategy_id,
                                                        account_name = order.account_name)
                elif order.order_type == OrderType.LIMIT_ORDER:
                    res = self.broker.place_limit_order(order.asset_name,order.units,order.limit,
                                                        cheat_on_close = order.cheat_on_close,
                                                        stop_loss_on_fill= order.stop_loss_on_fill,
                                                        stop_loss_limit_pct = order.stop_loss_limit_pct,
                                                        exchange_name = order.exchange_name,
                                                        strategy_id = self.strategy_id,
                                                        account_name = order.account_name)
                elif order.order_type == OrderType.STOP_LOSS_ORDER:
                    res = self.broker.place_stoploss_order(units = order.units,stop_loss = order.limit,asset_name = order.asset_name)
                assert(res.order_state != OrderState.BROKER_REJECTED)

        self.i += 1

spec = [
    ('broker_ptr',types.voidptr),
    ('exchange_ptr', types.voidptr),
    ('i',numba.int32)
]

@jitclass(spec)
class BenchMarkStrategy(Strategy):
    def __init__(self, broker_ptr : c_void_p, exchange_ptr : c_void_p) -> None:
        self.broker_ptr = broker_ptr 
        self.exchange_ptr = exchange_ptr
        self.i = 0
        
    def build(self):
        return
        
    def next(self):
        if self.i == 0:
            number_assets = Wrapper._asset_count(self.exchange_ptr)
            for j in range(0,number_assets):
                res = Wrapper._place_market_order(
                    self.broker_ptr,
                    j,
                    100,
                    True,
                    0
                )
            self.i += 1

if __name__ == "__main__":
    pass
