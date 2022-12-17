import time
from ctypes import *
import sys
from Asset import Asset
from Exchange import Exchange
from Broker import Broker

lib_path = r"C:\Users\bktor\Desktop\C++\FastTestLib\Debug\FASTTESTLIB.dll"
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

class FastTest:
    def __init__(self, exchange_ptr : c_void_p, broker_ptr : c_void_p, logging = True) -> None:
        self.ptr = _new_fastTest_ptr(exchange_ptr,broker_ptr,logging)

    def __del__(self):
        _free_fastTest_ptr(self.ptr)
    
    def forward_pass(self):
        return _fastTest_forward_pass(self.ptr)
    
    def backward_pass(self):
        _fastTest_backward_pass(self.ptr)

    def step(self):
        if not self.forward_pass(): return False
        self.backward_pass()
        return True

file_name = b"C:/Users/bktor/Desktop/Python/FastTest/tests/data/test2.csv"
new_asset = Asset(asset_name="test2")
new_asset.set_format("%d-%d-%d", 0, 1)
new_asset.load_from_csv(file_name)

exchange = Exchange()
exchange.register_asset(new_asset)
exchange.build()

broker = Broker(exchange.ptr)
ft = FastTest(exchange.ptr, broker.ptr, False)
while ft.step():
    print(exchange.get_market_price("test2"))
