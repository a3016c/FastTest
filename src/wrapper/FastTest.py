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
def run_slow(fast_test_ptr : c_void_p, strategy):
    while Wrapper._fastTest_forward_pass(fast_test_ptr):
        strategy.next()
        Wrapper._fastTest_backward_pass(fast_test_ptr)

@njit
def run_fast(fast_test_ptr : c_void_p, strategy):
    while Wrapper._fastTest_forward_pass(fast_test_ptr):
        strategy.next()
        Wrapper._fastTest_backward_pass(fast_test_ptr)

if __name__ == "__main__":
    exchange = Exchange()
    broker = Broker(exchange)
    for i in range (0,20):
        file_name = "C:/Users/bktor/test_large.csv"
        #file_name = r"C:\Users\bktor\Desktop\Python\FastTest\src\wrapper\tests\data\test2.csv"
        new_asset = Asset(exchange = exchange,asset_name=str(i))
        new_asset.set_format("%d-%d-%d", 0, 1)
        new_asset.load_from_csv(file_name)
        exchange.register_asset(new_asset)

    ft = FastTest(exchange, broker)
    ft.build()
    strategy = BenchMarkStrategy(exchange.ptr, broker.ptr)
    ft.add_strategy(strategy)

    st = time.time()
    run_fast(ft.ptr, strategy)
    et = time.time()
    print(f"FastTest run in : {(et-st)*1000} ms")



