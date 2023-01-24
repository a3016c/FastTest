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

from wrapper.Exchange import Exchange, Asset, g_asset_counter
from wrapper.Broker import Broker
from wrapper.Account import Account
from wrapper.Strategy import Strategy, BenchMarkStrategy, TestStrategy
from wrapper.Order import OrderSchedule, OrderType
from wrapper import Wrapper

class FastTest:
    def __init__(self, logging = False, debug = False) -> None:
        self.logging = logging
        self.debug = debug
        
        self.exchange_counter = 0
        self.broker_counter = 0
        self.strategy_counter = 0
        self.account_counter = 0
        
        self.accounts = {}
        
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
        
        if(exchange.is_registered()):
            raise Exception("Attempted to register an existing exchange")
        
        exchange.exchange_id = self.exchange_counter
        self.exchange_counter += 1
        if register: Wrapper._fastTest_register_exchange(self.ptr, exchange.ptr, exchange.exchange_id)
        
    def register_account(self, cash : float, account_name = "default"):
        
        if self.broker == None:
            raise Exception("No broker registered to place the account to")
        
        if cash < 0:
            raise Exception("Account must start with positive cash amount")
        
        if self.accounts.get(account_name) != None:
            raise Exception("Account with same name already exists")
        
        account_ptr = Wrapper._broker_register_account(self.broker.ptr, self.account_counter, cash)
        self.accounts[account_name] = Account(
                account_ptr = account_ptr,
                account_id = self.account_counter,
                account_name = account_name)
        self.account_counter += 1
        
    def register_broker(self, broker : Broker, register = True, account_name = "default"):
        self.broker = broker
        broker.broker_id = self.broker_counter
                
        self.accounts[account_name] = Account(
                account_ptr = Wrapper._get_account_ptr(self.broker.ptr, 0),
                account_id = self.account_counter,
                account_name = account_name)
        
        self.exchange_counter += 1
        self.account_counter += 1
                
        if register: Wrapper._fastTest_register_broker(self.ptr, broker.ptr, broker.broker_id)
        
    def get_benchmark_ptr(self):
        return Wrapper._get_benchmark_ptr(self.ptr)
    
    def add_strategy(self, strategy : Strategy):
        strategy.broker_ptr = self.broker.ptr
        strategy.strategy_id = self.strategy_counter
        self.strategy_counter += 1
        self.strategies = np.append(self.strategies,(strategy))

    def run(self):
        self.reset()
        for strategy in self.strategies:
            strategy.build()
        while self.step():
            pass
        
        self.metrics = Metrics(self)
    
    def step(self):
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
