import time
from ctypes import *
import sys
import os
import cProfile


import numpy as np
import pandas as pd
from numba import njit, jit

SCRIPT_DIR = os.path.dirname(__file__)
sys.path.append(os.path.dirname(SCRIPT_DIR))

from wrapper.Exchange import Exchange, Asset
from wrapper.Broker import Broker
from wrapper.Account import Account
from wrapper.Strategy import Strategy, BenchMarkStrategy, TestStrategy
from wrapper import Wrapper

class FastTest:
    def __init__(self, logging = False, debug = False) -> None:
        self.built = False
        self.logging = logging
        self.debug = debug
        
        #counters to set the necessary unique identifies for strucutres
        self.asset_counter = 0
        self.exchange_counter = 0
        self.broker_counter = 0
        self.strategy_counter = 0
        self.account_counter = 0
        
        #containers used to hold the various structures. Held here to ensure that the c pointers held in the
        #objects will not be freed untill the FastTest object is deleted
        self.assets = {}
        self.accounts = {}
        self.exchanges = {}
        
        self.benchmark = None
        self.broker = None
        self.strategies = np.array([], dtype="O")
                
        self.ptr = Wrapper._new_fastTest_ptr(self.logging,self.debug)
        
    def __del__(self):
        if self.debug: print("\nFREEING FASTTEST POINTER")
        Wrapper._free_fastTest_ptr(self.ptr)
        if self.debug: print("FASTTEST POINTER FREED\n")
        
    def profile(self):
        pr = cProfile.Profile()
        pr.enable()
        self.run()
        pr.disable()
        pr.print_stats(sort='time')

    def reset(self):
        Wrapper._fastTest_reset(self.ptr)

    def build(self):
        
        #copy the data into c++ objects and delete the local python copy to preserve memory
        for asset_name in list(self.assets.keys()):
            asset = self.assets[asset_name]
            exchange = self.exchanges[asset.exchange_name]
            exchange.register_asset(asset)
            del self.assets[asset_name]
        
        #allow the fasttest and broker to complete any nessecary setup
        Wrapper._build_fastTest(self.ptr)
        self.broker.build()
        
        for strategy in self.strategies:
            strategy.build()
            
        self.built = True
        
    def register_benchmark(self, asset : Asset):
        asset.asset_id = self.asset_counter
        asset.registered = True
        self.benchmark = asset
        self.asset_counter += 1
        asset.load_ptr()
        Wrapper._fastTest_register_benchmark(self.ptr, asset.ptr)
        
    def register_asset(self, asset_name : str, exchange_name = "default"):
        exchange = self.exchanges[exchange_name]
        
        #build a new asset object using the asset name and given exchange
        asset = Asset(exchange.exchange_id, asset_name, debug=self.debug, exchange_name=exchange_name)
        asset.asset_id = self.asset_counter
        asset.registered = True
        
        #once the asset has unique id we can allocate the c++ asset object
        asset.load_ptr()
                
        self.asset_counter += 1
        self.assets[asset_name] = asset
        return asset
        
    def register_exchange(self, exchange : Exchange, register = True):
        
        if(exchange.is_registered()):
            raise Exception("Attempted to register an existing exchange")
        
        exchange.exchange_id = self.exchange_counter
        self.exchanges[exchange.exchange_name] = exchange
        self.exchange_counter += 1
        if register: Wrapper._fastTest_register_exchange(self.ptr, exchange.ptr, exchange.exchange_id)
                
    def add_account(self, account_name : str, cash : float):
        if self.broker == None:
            raise Exception("No broker registered to place the account to")
        
        if self.accounts.get(account_name) != None:
            raise Exception("Account with same name already exists")
        
        if self.built:
            raise Exception("Account must be registered before FastTest is built")
                
        account = Account(self.account_counter, account_name, cash,
                          debug = self.debug)
        
        self.accounts[account.account_name] = account
        self.broker.account_map[account_name] = self.account_counter
        Wrapper._broker_register_account(self.broker.ptr, account.ptr)
        self.account_counter += 1
        
    def register_broker(self, broker : Broker,
                        register = True):
        self.broker = broker
        broker.broker_id = self.broker_counter
                
        self.exchange_counter += 1
                
        if register: Wrapper._fastTest_register_broker(self.ptr, broker.ptr, broker.broker_id)
        
    def get_benchmark_ptr(self):
        #return a pointer to a c++ asset class of the fasttest benchmark
        return Wrapper._get_benchmark_ptr(self.ptr)
    
    def add_strategy(self, strategy : Strategy):
        strategy.broker_ptr = self.broker.ptr
        strategy.strategy_id = self.strategy_counter
        self.strategy_counter += 1
        self.strategies = np.append(self.strategies,(strategy))

    def run(self):
        #clear any results/data from previous runs
        self.reset()
                
        while self.step():
            pass
        
    def load_metrics(self):
        self.metrics = Metrics(self)
        
    def step(self):
        """
        Core event loop. Allows the C++ code to handle all events emitted by the strategies. 
        
        Returns:
            bool: is there another time step to be executed in the current test
        """
    
        if not Wrapper._fastTest_forward_pass(self.ptr):
            return False
        for strategy in self.strategies:
            strategy.next()
        Wrapper._fastTest_backward_pass(self.ptr)
        return True
    
class Metrics():
    def __init__(self, ft : FastTest) -> None:
        self.broker = ft.broker
        self.positions = self.broker.get_position_history().to_df()
        
    def total_return(self):
        nlv = self.broker.get_nlv_history()
        return (nlv[-1] - nlv[0])/nlv[0]
        
    def position_count(self):
        return len(self.positions)
        
    def win_rate(self):
        wins_long = len(self.positions[(self.positions["units"] > 0) & (self.positions['realized_pl'] > 0)])
        win_pct_long = wins_long / len(self.positions[self.positions["units"] > 0])
        
        wins_short = len(self.positions[(self.positions["units"] > 0) & (self.positions['realized_pl'] > 0)])
        win_pct_short= wins_short / len(self.positions[self.positions["units"] < 0])
        
        win_pct = len(self.positions[self.positions["realized_pl"] > 0])/ len(self.positions)
        
        return win_pct*100, win_pct_long*100, win_pct_short*100
    
    def average_win(self):
        longs = self.positions[self.positions["units"] > 0]["realized_pl"].mean()
        shorts = self.positions[self.positions["units"] < 0]["realized_pl"].mean()
        return longs, shorts
    
    def position_duration(self):
        shorts = self.positions[self.positions["units"] < 0]
        longs = self.positions[self.positions["units"] > 0]
        
        avg_short_durations = (shorts["position_close_time"] - shorts["position_create_time"]).mean()
        avg_long_durations = (longs["position_close_time"] - longs["position_create_time"]).mean()
        avg_total_durations = (self.positions["position_close_time"] - self.positions["position_create_time"]).mean()

        return avg_total_durations, avg_long_durations, avg_short_durations
    
    def get_stats(self):
        win_pct, win_pct_long, win_pct_short = self.win_rate()
        avg_total_durations, avg_long_durations, avg_short_durations = self.position_duration()
        avg_pl_long, avg_pl_short = self.average_win()
        
        return (
            f"Number of Trades: {len(self.positions)}\n"
            f"Win Rate: {win_pct:.2f}\n"
            f"Long Win Rate: {win_pct_long:.2f}\n"
            f"Short Win Rate: {win_pct_short:.2f}\n"
            f"Average Long PL: {avg_pl_long:.2f}\n"
            f"Average Short PL: {avg_pl_short:.2f}\n"
            f"Average Trade Duration: {avg_total_durations}\n"
            f"Average Long Trade Duration {avg_long_durations}\n"
            f"Average Short Trade Duration: {avg_short_durations}\n\n"
            
        )
        
@jit(forceobj=True, cache=True)
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
