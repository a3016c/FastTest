from Broker import *
from ctypes import *
import sys 
import Wrapper
from Exchange import Exchange
from Order import OrderSchedule, OrderType
import numba
from numba.core import types
from numba.experimental import jitclass

#spec = [
#    ('broker_ptr',types.voidptr),
#    ('exchange_ptr', types.voidptr)
#]

#@jitclass(spec)
class Strategy():
    def __init__(self, broker_ptr : c_void_p, exchange_ptr : c_void_p) -> None:
        self.broker = broker_ptr 
        self.exchange_ptr = exchange_ptr

    def next(self):
        return 

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

    def next(self):
        if self.i == 0:
            number_assets = Wrapper._asset_count(self.exchange_ptr)
            for i in range(0,number_assets):
                Wrapper._place_market_order(
                    self.broker_ptr,
                    i,
                    100,
                    True
                )
            self.i += 1

class TestStrategy(Strategy):
    def __init__(self, order_schedule, broker = None, exchange = None) -> None:
        super().__init__(broker,exchange)
        self.order_schedule = order_schedule
        self.i = 0

    def next(self):
        for order in self.order_schedule:
            if order.i == self.i:
                if order.order_type == OrderType.MARKET_ORDER:
                    self.broker.place_market_order(order.asset_name,order.units,order.cheat_on_close)
                elif order.order_type == OrderType.LIMIT_ORDER:
                    self.broker.place_market_order(order.asset_name,order.units,order.limit,order.cheat_on_close)

        self.i += 1



if __name__ == "__main__":
    pass
