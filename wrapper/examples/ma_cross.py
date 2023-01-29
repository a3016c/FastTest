import sys
import os
from ctypes import c_char_p
import math
import time

import matplotlib.pyplot as plt

import backtrader as bt
from backtrader.analyzer import *
import backtrader.feeds as btfeeds

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from Exchange import Exchange
from Broker import Broker
from Strategy import *
from FastTest import FastTest

asset_count = 1000

class CustomDataLoader(btfeeds.PandasData):
    lines = ("slow_ma","fast_ma")

    params = (
        ('datetime',None),
        ("open", "CLOSE"),
        ('close', "CLOSE"),
        ('slow_ma', "slow_ma"),
        ('fast_ma', "fast_ma"),
        ('high', None),
        ('low', None),
        ('volume', None),
        ('openinterest', None),
    
    
    )
  
class CashMarket(bt.analyzers.Analyzer):
    """
    Analyzer returning cash and market values
    """

    def create_analysis(self):
        self.rets = {}
        self.vals = 0.0

    def notify_cashvalue(self, cash, value):
        self.vals = (
            self.strategy.datetime.datetime().strftime("%Y-%m-%d"),
            cash,
            value,
        )
        self.rets[len(self)] = self.vals

    def get_analysis(self):
        return self.rets

  
class BT_MA_Cross_Strategy(bt.Strategy):
    def __init__(self) -> None:
        super().__init__()
        self.index = 0
        self.slow_ma = 50
        self.fast_ma = 20
        self.position_size = .9 * (100000/asset_count)   
        self.o = []
        
    def notify_order(self, order):
        return
        # Check if an order has been completed
        if order.status in [order.Completed]:
            print(
                f"{self.datetime.datetime()} "
                f"{order.data._name:<6} {('BUY' if order.isbuy() else 'SELL'):<5} "
                f"Price: {order.executed.price:6.2f} "
                f"Value: {order.executed.value:6.2f} "
                f"Comm: {order.executed.comm:4.4f} "
                f"Size: {order.created.size:9.4f} "
            )

        if not order.alive() and order in self.o:
            self.o.remove(order)   
        
    def next(self):
        
        if self.index < self.slow_ma:
            self.index += 1
            return
        
        slow_ma_dict = {d : d.slow_ma[0] for d in self.datas}
        fast_ma_dict = {d : d.fast_ma[0] for d in self.datas}
        
        for d in slow_ma_dict:
            if not self.getposition(d).size:
                
                market_price = d.close[0]
                units = self.position_size / market_price
                if fast_ma_dict[d] < slow_ma_dict[d]:
                    self.sell(data=d, size = units)
                else:
                    self.buy(data=d, size = units)
                                    
            else:
                position_units = self.getposition(d).size
                fast = fast_ma_dict[d]
                slow = slow_ma_dict[d]
                
                #position is in right direction
                if fast < slow and position_units < 0:
                    continue
                elif fast > slow and position_units > 0:
                    continue
                #close existing position
                else:
                    if position_units > 0:
                        self.sell(data=d, size = position_units)
                    else:
                        self.buy(data=d, size = position_units)
  
class MA_Cross_Strategy(Strategy):
    def __init__(self, broker: Broker, exchange: Exchange, ft: FastTest, slow_ma : int, fast_ma : int) -> None:
        super().__init__(broker, exchange)
        self.ft = ft
        self.candle_count = 0
        self.slow_ma = slow_ma
        self.fast_ma = fast_ma
        self.load(asset_count)
        
    def build(self):
        self.asset_names = self.exchange.id_map.values()
        self.position_size = .9 * (100000/asset_count)
        
    def next(self):
        #pull in the data needed to calcuate moving average crossovers
        slow_ma_dict = {asset_name : self.exchange.get(asset_name, "slow_ma") for asset_name in self.asset_names}
        fast_ma_dict = {asset_name : self.exchange.get(asset_name, "fast_ma") for asset_name in self.asset_names}

        for key in slow_ma_dict:
            #check to see if the asset is currently tradeable
            if not math.isnan(slow_ma_dict[key]):
                #check to see if a position with the same asset currently exists
                if not self.broker.position_exists(key,self.exchange.exchange_name):
                    
                    market_price = self.exchange.get_market_price(key)
                    units = self.position_size / market_price
                    
                    if fast_ma_dict[key] < slow_ma_dict[key]:
                        units *= -1
                        
                    self.broker.place_market_order(key, units)
                    
                else:
                    #get the open position with the same asset name
                    position = self.broker.get_position(key, self.exchange.exchange_name)
                    fast = fast_ma_dict[key]
                    slow = slow_ma_dict[key]
                    
                    #position is in right direction
                    if fast < slow and position.units < 0:
                        continue
                    elif fast > slow and position.units > 0:
                        continue                    
                    #close existing position
                    else:
                        units = -1 * position.units
                        self.broker.place_market_order(key, units)
                        
    def load(self, n_assets):
        n_steps = 500
        for i in range(n_assets):
            new_asset = self.ft.register_asset(str(i))
            new_asset.set_format("%d-%d-%d", 0, 0)
            new_asset_df = new_asset.generate_random(step_size = .1, num_steps = n_steps)
            new_asset_df["slow_ma"] = new_asset_df["CLOSE"].rolling(window = self.slow_ma).mean()
            new_asset_df["fast_ma"] = new_asset_df["CLOSE"].rolling(window = self.fast_ma).mean()
            new_asset.load_from_df(new_asset_df, nano = True)
            new_asset.set_warmup(self.slow_ma)
            self.candle_count += n_steps
            
if __name__ == "__main__":
    #-----------------------------------------------------------------------------
    #----FASTTEST----
    #-----------------------------------------------------------------------------
    st = time.time()
    ft = FastTest(logging=False, debug=False)
    exchange = Exchange()
    ft.register_exchange(exchange)
    
    broker = Broker(exchange, logging=False)
    ft.register_broker(broker)
    ft.add_account("default",100000)
    
    ma_cross_strategy = MA_Cross_Strategy(broker, exchange, ft, slow_ma = 50, fast_ma = 20)    
    ft.add_strategy(ma_cross_strategy)
    
    ft.build()
    et = time.time()
    print(f"\n\nFastTest built in {et-st:.5f} seconds")
    
    st = time.time()
    ft.run()
    et = time.time()
    cps_ft = ma_cross_strategy.candle_count / (et-st)
    print(f"FastTest completed in {et-st:.6f} seconds")
    print(f"FastTest candles per seconds: {cps_ft:.2f}\n")  
      
    #-----------------------------------------------------------------------------
    #----BACKTRADER----
    #-----------------------------------------------------------------------------
    st = time.time()
    cerebro = bt.Cerebro()
    cerebro.addstrategy(BT_MA_Cross_Strategy)   
    
    cerebro.broker.setcash(100000.0)
    cerebro.addobserver(bt.observers.Broker)
    cerebro.addobserver(bt.observers.Trades)
    cerebro.addobserver(bt.observers.BuySell)
    cerebro.addanalyzer(CashMarket, _name="cash_market")

    for key in ft.assets:
        df = ft.assets[key].df()
        df.index = pd.to_datetime(df.index, unit = "s")
        data = CustomDataLoader(
            dataname = df,           
            timeframe=bt.TimeFrame.Seconds,
        )
        data.plotinfo.plot = False
        cerebro.adddata(data, name=key)

    et = time.time()
    print(f"Backtrader built in: {et-st:.5f} seconds")    

    st = time.time()
    results = cerebro.run()
    et = time.time()
    
    cps_bt = ma_cross_strategy.candle_count / (et-st)
    print(f"Backtrader completed in {et-st:.6f} seconds")
    print(f"Backtrader candles per seconds: {cps_bt:.2f}")     
    print(f"\n\nFastTest {cps_ft / cps_bt:.2f}x faster")
    
    print('Backtrader Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print('FastTest Final Portfolio Value: %.2f' % broker.get_nlv_history()[-1])
    
    dictionary = results[0].analyzers.getbyname("cash_market").get_analysis()
    df = pd.DataFrame(dictionary).T
    df.columns = ["Date", "BT Cash", "BT Value"]
    
    datetime_epoch_index = ft.get_datetime_index()
    df.index = pd.to_datetime(datetime_epoch_index, unit = "s")
    df["FT Value"] = broker.get_nlv_history()
    
    fig, ax = plt.subplots(figsize=(10.5, 6.5))
    ax.plot(df.index, df["BT Value"], label = "Backtrader NLV")  
    ax.plot(df.index, df["FT Value"] + 1, label = "FastTest NLV")
    
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
          ncol=3, fancybox=True, shadow=True)
    
    print(df)
    plt.show()
    