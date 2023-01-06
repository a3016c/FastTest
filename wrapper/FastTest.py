import time
from ctypes import *
import sys
import cProfile
import numpy as np
import pandas as pd
from numba import njit, jit

from Exchange import Exchange, Asset
from Broker import Broker
from Strategy import Strategy, BenchMarkStrategy, TestStrategy
from Order import OrderSchedule, OrderType
import Wrapper

class FastTest:
    def __init__(self, exchange : Exchange, broker : Broker, logging = False) -> None:
        self.logging = logging
        self.exchange = exchange
        self.exchange_ptr = exchange.ptr
        self.broker = broker
        self.broker_ptr = broker.ptr
        self.benchmark = None
        self.strategies = np.array([], dtype="O")

    def __del__(self):
        try:
            Wrapper._free_fastTest_ptr(self.ptr)
        except:
            pass
        
    def profile(self):
        cProfile.runctx('self.run()', globals(), locals())

    def reset(self):
        Wrapper._fastTest_reset(self.ptr)

    def build(self):
        self.exchange.build()
        self.broker.build()
        self.ptr = Wrapper._new_fastTest_ptr(self.exchange_ptr,self.broker_ptr,self.logging)
        
    def register_benchmark(self, asset : Asset):
        self.benchmark = asset
        Wrapper._fastTest_register_benchmark(self.ptr, asset.ptr)
        
    def get_benchmark_ptr(self):
        return Wrapper._get_benchmark_ptr(self.ptr)
    
    def add_strategy(self, strategy : Strategy):
        strategy.broker_ptr = self.broker_ptr
        strategy.exchange_ptr = self.exchange_ptr
        self.strategies = np.append(self.strategies,(strategy))

    def run(self):
        self.reset()
        for strategy in self.strategies:
            strategy.build()
        while self.step():
            pass
    
    def step(self):
        if not Wrapper._fastTest_forward_pass(self.ptr):
            return False
        for strategy in self.strategies:
            strategy.next()
        Wrapper._fastTest_backward_pass(self.ptr)
        return True

@jit(forceobj=True)
def run_jit(fast_test_ptr : c_void_p, strategy):
    Wrapper._fastTest_reset(fast_test_ptr)
    strategy.build()
    while Wrapper._fastTest_forward_pass(fast_test_ptr):
        strategy.next()
        Wrapper._fastTest_backward_pass(fast_test_ptr)
        
def test_speed():
    exchange = Exchange()
    broker = Broker(exchange)
    ft = FastTest(exchange, broker)
    
    n = 200000
    n_assets = 20
    
    o = np.arange(0,10,step = 10/n).astype(np.float32)
    c = (np.arange(0,10,step = 10/n) + .001).astype(np.float32)
    index = pd.date_range(end='1/1/2018', periods=n, freq = "s").astype(int) / 10**9
    df = pd.DataFrame(data = [o,c]).T
    df.columns = ["OPEN","CLOSE"]
    df.index = index
    st = time.time()
    for i in range(0,n_assets):    
        new_asset = Asset(exchange, asset_name=str(i))
        new_asset.set_format("%d-%d-%d", 0, 1)
        new_asset.load_from_df(df)
        ft.exchange.register_asset(new_asset)
    et = time.time()
    print(f"Average Asset Load Time: {(et-st)*(1000/n_assets):.2f} ms")

    strategy = BenchMarkStrategy(broker.ptr, exchange.ptr)
        
    ft.build()
    ft.add_strategy(strategy)
    st = time.time()
    ft.run()
    et = time.time()
    print("=========SIMPLE RUN=========")
    print(f"FastTest run in: {(et-st):.2f} Seconds")
    print(f"Candles Per Second: {n*n_assets/(et-st):,.2f}")
    print("============================")
    
    ft = FastTest(exchange, broker)
    ft.build()
    st = time.time()
    run_jit(ft.ptr, strategy)
    et = time.time()
    
    print("=========JIT RUN=========")
    print(f"FastTest run in: {(et-st):.2f} Seconds")
    print(f"Candles Per Second: {n*n_assets/(et-st):,.2f}")
    print("============================")

if __name__ == "__main__":
    test_speed()
