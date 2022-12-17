from Broker import *
from ctypes import *
import sys 

class Strategy():
    def __init__(self, lib_path : str, broker = None) -> None:
        self.broker = broker
        
        try:
            FastTest = CDLL(lib_path)
        except OSError:
            print("Unable to load the system C library")
            sys.exit()

        self._place_market_order = FastTest.place_market_order
        self._place_market_order.argtypes = [c_void_p, c_char_p, c_float, c_bool]
        self._place_market_order.restype = c_uint

    def place_market_order(self, asset_name : str, units : float, cheat_on_close = False):
        return OrderState(self._place_market_order(
            self.broker,
            c_char_p(asset_name.encode("utf-8")),
            units,
            cheat_on_close
            )
        )

    def next():
        return 

class BenchMarkStrategy(Strategy):
    def __init__(self, lib_path : str, broker = None) -> None:
        super().__init__(lib_path, broker)
        self.i = 0

    def next(self):
        if self.i == 0:
            res = self.place_market_order("0",100)
            res = self.place_market_order("1",100)
            res = self.place_market_order("2",100)
            res = self.place_market_order("3",100)
            res = self.place_market_order("4",100)
            print(res)
        self.i += 1