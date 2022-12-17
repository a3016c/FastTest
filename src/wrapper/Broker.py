import sys
from ctypes import *
from Asset import Asset

lib_path = r"C:\Users\bktor\Desktop\C++\FastTestLib\Debug\FASTTESTLIB.dll"
try:
    FastTest = CDLL(lib_path)
except OSError:
    print("Unable to load the system C library")
    sys.exit()

"""Broker wrapper"""
_new_broker_ptr = FastTest.CreateBrokerPtr
_new_broker_ptr.argtypes =[c_void_p, c_bool]
_new_broker_ptr.restype = c_void_p
"""====================================="""
_free_broker_ptr = FastTest.CreateBrokerPtr
_free_broker_ptr.argtypes = [c_void_p]
"""====================================="""
_reset_broker = FastTest.reset_broker
_reset_broker.argtypes = [c_void_p]

class Broker():
    def __init__(self, exchange_ptr : c_void_p, logging = True) -> None:
        self.ptr = _new_broker_ptr(exchange_ptr, logging)

    def __del__(self):
        _free_broker_ptr(self.ptr)

    def reset(self):
        _reset_broker(self.ptr)