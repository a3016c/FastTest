import time
from ctypes import *
import sys
import numpy as np
from Asset import Asset
from Exchange import Exchange
from Broker import Broker
from Strategy import Strategy, BenchMarkStrategy
import LibWrapper



class FastTest:
    def __init__(self, logging = False) -> None:
        self.logging = logging
        self.exchange = Exchange()
        self.exchange_ptr = self.exchange.ptr
        self.strategies = np.array([], dtype="O")

    def __del__(self):
        LibWrapper._free_fastTest_ptr(self.ptr)

    def reset(self):
        LibWrapper._fastTest_reset(self.ptr)

    def build(self):
        self.exchange.build()
        self.broker = Broker(self.exchange.ptr)
        self.broker_ptr = self.broker.ptr
        self.ptr = LibWrapper._new_fastTest_ptr(self.exchange_ptr,self.broker_ptr,self.logging)

    def add_strategy(self, strategy : Strategy):
        strategy.build(self.broker,self.exchange)
        self.strategies = np.append(self.strategies,(strategy))

    def run(self):
        while self.step():
            pass

    def step(self):
        if not LibWrapper._fastTest_forward_pass(self.ptr):
            return False
        for strategy in self.strategies:
            strategy.next()
        LibWrapper._fastTest_backward_pass(self.ptr)
        return True

if __name__ == "__main__":
    ft = FastTest()
    for i in range (0,5):
        file_name = "C:/Users/bktor/test_large.csv"
        #file_name = r"C:\Users\bktor\Desktop\Python\FastTest\src\wrapper\tests\data\test2.csv"
        new_asset = Asset(asset_name=str(i))
        new_asset.set_format("%d-%d-%d", 0, 1)
        new_asset.load_from_csv(file_name)
        ft.exchange.register_asset(new_asset)

    ft.build()
    strategy = BenchMarkStrategy()
    ft.add_strategy(strategy)

    st = time.time()
    ft.run()
    et = time.time()
    print(f"FastTest run in : {(et-st)*1000} ms")



