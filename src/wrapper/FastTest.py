import time
from ctypes import *
import sys
import numpy as np
from numba import njit, jit

from Exchange import Exchange, Asset
from Broker import Broker
from Strategy import Strategy, BenchMarkStrategy
import Wrapper


class FastTest:
    def __init__(self, exchange : Exchange, broker : Broker, logging = False) -> None:
        self.logging = logging
        self.exchange = exchange
        self.exchange_ptr = exchange.ptr
        self.broker = broker
        self.broker_ptr = broker.ptr
        self.strategies = np.array([], dtype="O")

    def __del__(self):
        try:
            Wrapper._free_fastTest_ptr(self.ptr)
        except:
            pass

    def reset(self):
        Wrapper._fastTest_reset(self.ptr)

    def build(self):
        self.exchange.build()
        self.ptr = Wrapper._new_fastTest_ptr(self.exchange_ptr,self.broker_ptr,self.logging)

    def add_strategy(self, strategy : Strategy):
        strategy.broker_ptr = self.broker_ptr
        strategy.exchange_ptr = self.exchange_ptr
        self.strategies = np.append(self.strategies,(strategy))

    def run(self):
        while self.step():
            pass
    
    def step(self):
        if not Wrapper._fastTest_forward_pass(self.ptr):
            return False
        for strategy in self.strategies:
            strategy.next()
        Wrapper._fastTest_backward_pass(self.ptr)
        return True

@jit
def run_jit(fast_test_ptr : c_void_p, strategy):
    while Wrapper._fastTest_forward_pass(fast_test_ptr):
        strategy.next()
        Wrapper._fastTest_backward_pass(fast_test_ptr)

@njit
def run_njit(fast_test_ptr : c_void_p, strategy):
    while Wrapper._fastTest_forward_pass(fast_test_ptr):
        strategy.next()
        Wrapper._fastTest_backward_pass(fast_test_ptr)

if __name__ == "__main__":
    order_count = 2
    order_history = Wrapper.OrderHistoryStruct(order_count)
    print(order_history.ORDER_ARRAY[0].contents)
    #order_struct_pointer = pointer(order_history)
