import time
from ctypes import *
import sys
import cProfile
import numpy as np
import pandas as pd
from numba import njit, jit


from Exchange import Exchange, Asset, g_asset_counter
from Broker import Broker
from Strategy import Strategy, BenchMarkStrategy, TestStrategy
from Order import OrderSchedule, OrderType
import Wrapper

class FastTest:
    def __init__(self, logging = False, debug = False) -> None:
        self.logging = logging
        self.debug = debug
        self.exchange_counter = 0
        self.broker_counter = 0
        self.benchmark = None
        self.broker = None
        self.strategies = np.array([], dtype="O")
        
        g_asset_counter = 0 
        
        self.ptr = Wrapper._new_fastTest_ptr(self.logging,self.debug)
        
    def __del__(self):
        try:
            Wrapper._free_fastTest_ptr(self.ptr)
        except:
            pass
        
    def profile(self):
        pr = cProfile.Profile()
        pr.enable()
        self.run()
        pr.disable()
        pr.print_stats(sort='time')

    def reset(self):
        Wrapper._fastTest_reset(self.ptr)

    def build(self):
        Wrapper._build_fastTest(self.ptr)
        self.broker.build()
        
    def register_benchmark(self, asset : Asset):
        self.benchmark = asset
        Wrapper._fastTest_register_benchmark(self.ptr, asset.ptr)
        
    def register_exchange(self, exchange : Exchange, register = True):
        exchange.exchange_id = self.exchange_counter
        self.exchange_counter += 1
        if register: Wrapper._fastTest_register_exchange(self.ptr, exchange.ptr, exchange.exchange_id)
        
    def register_broker(self, broker : Broker, register = True):
        self.broker = broker
        broker.broker_id = self.broker_counter
        self.exchange_counter += 1
        if register: Wrapper._fastTest_register_broker(self.ptr, broker.ptr, broker.broker_id)
        
    def get_benchmark_ptr(self):
        return Wrapper._get_benchmark_ptr(self.ptr)
    
    def add_strategy(self, strategy : Strategy):
        strategy.broker_ptr = self.broker.ptr
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
    n_assets = 40
    
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
