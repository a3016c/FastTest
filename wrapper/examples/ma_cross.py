import sys
import os
from ctypes import c_char_p
import math
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from Exchange import Exchange
from Broker import Broker
from Strategy import *
from FastTest import FastTest

class MA_Cross_Strategy(Strategy):
    def __init__(self, broker: Broker, exchange: Exchange, ft: FastTest, slow_ma : int, fast_ma : int) -> None:
        super().__init__(broker, exchange)
        self.ft = ft
        self.candle_count = 0
        self.slow_ma = slow_ma
        self.fast_ma = fast_ma
        self.load(10)
        
    def build(self):
        self.asset_names = self.exchange.id_map.values()
        self.asset_count = len(self.exchange.asset_map)
        self.position_size = .9 * (100000/self.asset_count)
        
    def next(self):
        slow_ma_dict = {asset_name : self.exchange.get(asset_name, "slow_ma") for asset_name in self.asset_names}
        fast_ma_dict = {asset_name : self.exchange.get(asset_name, "fast_ma") for asset_name in self.asset_names}

        for key in slow_ma_dict:
            if not math.isnan(slow_ma_dict[key]):
                if not self.broker.position_exists(key,self.exchange.exchange_name):
                    
                    market_price = self.exchange.get_market_price(key)
                    units = self.position_size / market_price
                    
                    if fast_ma_dict[key] < slow_ma_dict[key]:
                        units *= -1
                        
                    self.broker.place_market_order(key, units, exchange_name = self.exchange.exchange_name)
                    
                else:
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
                        self.broker.place_market_order(key, units, exchange_name=self.exchange.exchange_name)
                        
    def load(self, n_assets):
        n_steps = 2000
        for i in range(n_assets):
            new_asset = self.ft.register_asset(str(i))
            new_asset.set_format("%d-%d-%d", 0, 0)
            new_asset_df = new_asset.generate_random(step_size = .01, num_steps = n_steps)
            new_asset_df["slow_ma"] = new_asset_df["CLOSE"].rolling(window = self.slow_ma).mean()
            new_asset_df["fast_ma"] = new_asset_df["CLOSE"].rolling(window = self.fast_ma).mean()
            new_asset.load_from_df(new_asset_df, nano = True)
            new_asset.set_warmup(self.slow_ma)
            self.candle_count += n_steps
        print(new_asset_df)
            
if __name__ == "__main__":
    ft = FastTest(logging=False, debug=False)
    exchange = Exchange()
    ft.register_exchange(exchange)
    
    broker = Broker(exchange, logging=False)
    ft.register_broker(broker)
    ft.add_account("default",100000)
    
    ma_cross_strategy = MA_Cross_Strategy(broker, exchange, ft, 20, 50)    
    ft.add_strategy(ma_cross_strategy)
    
    ft.build()
    
    st = time.time()
    ft.run()
    et = time.time()
    
    print(ma_cross_strategy.candle_count / (et-st))
    
    datetime_epoch_index = ft.get_datetime_index()
    datetime_index = pd.to_datetime(datetime_epoch_index, unit = "s")
    print(datetime_index)
    #ft.plot()            
