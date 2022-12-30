from Broker import *
from ctypes import *
import sys 
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

import numba
from numba.core import types
from numba.experimental import jitclass

from Exchange import Exchange
from Order import OrderSchedule, OrderType
import Wrapper

class Strategy():
    def __init__(self, broker : Broker, exchange : Exchange) -> None:
        self.broker = broker 
        self.exchange = exchange
        
    def build(self):
        return

    def next(self):
        return 
    
    def plot(self):
        nlv = self.broker.get_nlv_history()
        roll_max = np.maximum.accumulate(nlv)
        daily_drawdown = nlv / roll_max - 1.0
        max_drawdown = np.minimum.accumulate(daily_drawdown) * 100
        
        datetime_epoch_index = self.exchange.get_datetime_index()
        datetime_index = pd.to_datetime(datetime_epoch_index, unit = "s")
        
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios = [1,3])
        fig = matplotlib.pyplot.gcf()
        fig.set_size_inches(10.5, 6.5, forward = True)
        
        ax2.plot(datetime_index, nlv)
        ax2.set_ylabel("NLV")
        ax2.set_xlabel("Datetime")
        
        ax1.plot(datetime_index, max_drawdown)
        ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
        ax1.set_ylabel("Max Drawdown")
        
        plt.show()

class TestStrategy(Strategy):
    def __init__(self, order_schedule, broker = None, exchange = None) -> None:
        super().__init__(broker,exchange)
        self.order_schedule = order_schedule
        self.i = 0
        
    def build():
        return

    def next(self):
        for order in self.order_schedule:
            if order.i == self.i:
                if order.order_type == OrderType.MARKET_ORDER:
                    res = self.broker.place_market_order(order.asset_name,order.units,order.cheat_on_close)
                elif order.order_type == OrderType.LIMIT_ORDER:
                    res = self.broker.place_limit_order(order.asset_name,order.units,order.limit,order.cheat_on_close)
                elif order.order_type == OrderType.STOP_LOSS_ORDER:
                    res = self.broker.place_stoploss_order(units = order.units,stop_loss = order.limit,asset_name = order.asset_name)
                assert(res != OrderState.BROKER_REJECTED)

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
                    True
                )
            self.i += 1

if __name__ == "__main__":
    pass
