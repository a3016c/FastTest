import time
from ctypes import *
import sys
import numpy as np
from Asset import Asset
from Exchange import Exchange
from Broker import Broker
from Strategy import Strategy, BenchMarkStrategy

lib_path = r"C:\Users\bktor\Desktop\C++\FastTestLib\x64\Release\FASTTESTLIB.dll"
try:
    FastTest = CDLL(lib_path)
except OSError:
    print("Unable to load the system C library")
    sys.exit()

"""FastTest wrapper"""
_new_fastTest_ptr = FastTest.CreateFastTestPtr
_new_fastTest_ptr.argtypes = [c_void_p, c_void_p, c_bool]
_new_fastTest_ptr.restype = c_void_p
"""====================================="""
_free_fastTest_ptr = FastTest.DeleteFastTestPtr
_free_fastTest_ptr.argtypes = [c_void_p]
"""====================================="""
_fastTest_forward_pass = FastTest.forward_pass
_fastTest_forward_pass.argtypes = [c_void_p]
_fastTest_forward_pass.restype = c_bool
"""====================================="""
_fastTest_backward_pass = FastTest.backward_pass
_fastTest_backward_pass.argtypes = [c_void_p]

_fastTest_test = FastTest.test_speed
_fastTest_test.argtypes = [c_void_p]

class FastTest:
    def __init__(self, lib_path : str, logging = False) -> None:
        self.logging = logging
        self.exchange = Exchange(lib_path)
        self.exchange_ptr = self.exchange.ptr
        self.strategies = np.array([], dtype="O")

    def __del__(self):
        _free_fastTest_ptr(self.ptr)

    def build(self):
        self.exchange.build()
        self.broker = Broker(lib_path, self.exchange.ptr)
        self.broker_ptr = self.broker.ptr
        self.ptr = _new_fastTest_ptr(self.exchange_ptr,self.broker_ptr,self.logging)

    def add_strategy(self, strategy : Strategy):
        strategy.broker = self.broker_ptr
        self.strategies = np.append(self.strategies,(strategy))

    def run(self):
        while self.step():
            pass

    def step(self):
        if not _fastTest_forward_pass(self.ptr):
            return False
        for strategy in self.strategies:
            strategy.next()
        _fastTest_backward_pass(self.ptr)
        return True

if __name__ == "__main__":
    lib_path = r"C:\Users\bktor\Desktop\C++\FastTestLib\x64\Release\FASTTESTLIB.dll"
    ft = FastTest(lib_path=lib_path)
    for i in range (0,5):
        file_name = b"C:/Users/bktor/test_large.csv"
        file_name = b"C:/Users/bktor/Desktop/Python/FastTest/tests/data/test2.csv"
        new_asset = Asset(lib_path, asset_name=str(i))
        new_asset.set_format("%d-%d-%d", 0, 1)
        new_asset.load_from_csv(file_name)
        ft.exchange.register_asset(new_asset)

    ft.build()
    strategy = BenchMarkStrategy(lib_path=lib_path)
    ft.add_strategy(strategy)

    st = time.time()
    ft.run()
    et = time.time()
    print(f"FastTest run in : {(et-st)*1000} ms")



