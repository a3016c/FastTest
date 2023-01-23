from ctypes import *
import sys 
import os

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.offsetbox import AnchoredText

import numba
from numba.core import types
from numba.experimental import jitclass

SCRIPT_DIR = os.path.dirname(__file__)
sys.path.append(os.path.dirname(SCRIPT_DIR))

from wrapper.Exchange import Exchange
from wrapper.Broker import Broker
from wrapper.Order import OrderSchedule, OrderType, OrderState
from wrapper import Wrapper

class Strategy():
    def __init__(self, broker : Broker, exchange : Exchange, strategy_name = "default") -> None:
        self.broker = broker 
        self.exchange = exchange
        self.strategy_name = strategy_name
        self.strategy_id = None
        
    def build(self):
        return

    def next(self):
        return 
                     
    def close_positions(self):
        positions = self.broker.get_positions()
        for i in range(positions.number_positions):
            position = positions.POSITION_ARRAY[i].contents
            asset_name = self.exchange.id_map[position.asset_id]
            self.broker.place_market_order(asset_name, -1*position.units)
    
    def get_sharpe(self, nlvs, N = 255, rf = .01):
        returns = np.diff(nlvs) / nlvs[:-1]
        sharpe = returns.mean() / returns.std()
        sharpe = (252**.5)*sharpe
        return round(sharpe,3)
        
    
    def plot(self, benchmark = None):
        nlv = self.broker.get_nlv_history()
        roll_max = np.maximum.accumulate(nlv)
        daily_drawdown = nlv / roll_max - 1.0
        
        datetime_epoch_index = self.exchange.get_datetime_index()
        datetime_index = pd.to_datetime(datetime_epoch_index, unit = "s")
        
        backtest_df = pd.DataFrame(index = datetime_index, data = nlv, columns=["nlv"])
        backtest_df["max_drawdown"] = np.minimum.accumulate(daily_drawdown) * 100
                    
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios = [1,3])
        fig = matplotlib.pyplot.gcf()
        fig.set_size_inches(10.5, 6.5, forward = True)
                    
        if benchmark != None:
            benchmark_df = benchmark.df()
            benchmark_df = benchmark_df[["CLOSE"]]
            benchmark_df.rename({'CLOSE': 'Benchmark'}, axis=1, inplace=True)
            
            benchmark_df.index = pd.to_datetime(benchmark_df.index, unit = "s")
            backtest_df = pd.merge(backtest_df,benchmark_df, how='inner', left_index=True, right_index=True)

            ratio = nlv[0] / backtest_df["Benchmark"].values[0]
            backtest_df["Benchmark"] = backtest_df["Benchmark"].apply(lambda x: x*ratio)

            ax2.plot(datetime_index, backtest_df["Benchmark"], color = "black", label = "Benchmark")  
        
        ax2.plot(datetime_index, backtest_df["nlv"], label = "NLV")
        ax2.set_ylabel("NLV")
        ax2.set_xlabel("Datetime")
        ax2.legend()
        
        ax1.plot(datetime_index, backtest_df["max_drawdown"])
        ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
        ax1.set_ylabel("Max Drawdown")
        
        sharpe = self.get_sharpe(backtest_df["nlv"].values)
        corr = round(np.corrcoef(
            backtest_df["nlv"].values, 
            backtest_df["Benchmark"].values, 
            rowvar = False)[0][1],3)
        
        metrics = f"Sharpe: {sharpe} \n Benchmark Corr: {corr}"
        anchored_text = AnchoredText(metrics, loc=3)
        ax2.add_artist(anchored_text)
                
        plt.show()

class TestStrategy(Strategy):
    def __init__(self, order_schedule, broker = None, exchange = None, strategy_name = "default") -> None:
        super().__init__(broker,exchange,strategy_name)
        self.order_schedule = order_schedule
        self.i = 0
        
    def build(self):
        return

    def next(self):
        for order in self.order_schedule:
            if order.i == self.i:
                if order.order_type == OrderType.MARKET_ORDER:
                    res = self.broker.place_market_order(order.asset_name,order.units,
                                                        cheat_on_close = order.cheat_on_close,
                                                        stop_loss_on_fill= order.stop_loss_on_fill,
                                                        stop_loss_limit_pct = order.stop_loss_limit_pct,
                                                        exchange_name = order.exchange_name,
                                                        strategy_id = self.strategy_id,
                                                        account_id = order.account_id)
                elif order.order_type == OrderType.LIMIT_ORDER:
                    res = self.broker.place_limit_order(order.asset_name,order.units,order.limit,
                                                        cheat_on_close = order.cheat_on_close,
                                                        stop_loss_on_fill= order.stop_loss_on_fill,
                                                        stop_loss_limit_pct = order.stop_loss_limit_pct,
                                                        exchange_name = order.exchange_name,
                                                        strategy_id = self.strategy_id,
                                                        account_id = order.account_id)
                elif order.order_type == OrderType.STOP_LOSS_ORDER:
                    res = self.broker.place_stoploss_order(units = order.units,stop_loss = order.limit,asset_name = order.asset_name)
                assert(res.order_state != OrderState.BROKER_REJECTED)

        self.i += 1

spec = [
    ('broker_ptr',types.voidptr),
    ('exchange_ptr', types.voidptr),
    ('i',numba.int32)
]

@jitclass(spec)
class BenchMarkStrategy(Strategy):
    def __init__(self, broker_ptr : c_void_p, exchange_ptr : c_void_p) -> None:
        self.broker_ptr = broker_ptr 
        self.exchange_ptr = exchange_ptr
        self.i = 0
        
    def build(self):
        return
        
    def next(self):
        if self.i == 0:
            number_assets = Wrapper._asset_count(self.exchange_ptr)
            for j in range(0,number_assets):
                res = Wrapper._place_market_order(
                    self.broker_ptr,
                    j,
                    100,
                    True,
                    0
                )
            self.i += 1

if __name__ == "__main__":
    pass
