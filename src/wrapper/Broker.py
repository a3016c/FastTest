import sys
from ctypes import *
from Asset import Asset
from enum import Enum

class OrderState(Enum):
	ACCEPETED = 0
	OPEN = 1
	FILLED = 2
	CANCELED = 3
	BROKER_REJECTED = 4

class Broker():
    def __init__(self, lib_path, exchange_ptr : c_void_p, logging = True) -> None:
        try:
            FastTest = CDLL(lib_path)
        except OSError:
            print("Unable to load the system C library")
            sys.exit()
        """Broker wrapper"""
        self._new_broker_ptr = FastTest.CreateBrokerPtr
        self._new_broker_ptr.argtypes =[c_void_p, c_bool]
        self._new_broker_ptr.restype = c_void_p
        """====================================="""
        self._free_broker_ptr = FastTest.CreateBrokerPtr
        self._free_broker_ptr.argtypes = [c_void_p]
        """====================================="""
        self._reset_broker = FastTest.reset_broker
        self._reset_broker.argtypes = [c_void_p]
        """====================================="""


        self.ptr = self._new_broker_ptr(exchange_ptr, logging)

    def __del__(self):
        self._free_broker_ptr(self.ptr)

    def reset(self):
        self._reset_broker(self.ptr)