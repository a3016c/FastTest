import sys
import os
import time
import zipfile
import io
from math import isnan

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import numpy as np
from numba import jit
from Exchange import Exchange, Asset
from Broker import Broker
from Strategy import *
from FastTest import FastTest

class Agis_Strategy(Strategy):
    def __init__(self, broker: Broker, exchange: Exchange, ft : FastTest, lookahead : int) -> None:
        super().__init__(broker, exchange)
        self.zip_path = "/Users/nathantormaschy/Downloads/preds_test.zip"
        self.ft = ft
        self.load()
        self.i = 0
        self.lookahead = lookahead
        self.position_size = .025
        self.position_count = 2
        
    def build(self):
        self.asset_names = self.exchange.id_map.values()
        self.asset_ids = self.exchange.asset_map.values()
    
    def check_positions(self):
        positions = self.broker.get_positions()
        for i in range(positions.number_positions):
            position = positions.POSITION_ARRAY[i].contents
            if position.bars_held == self.lookahead:
                asset_name = self.exchange.id_map[position.asset_id]
                self.broker.place_market_order(asset_name, -1*position.units,
                                            exchange_name="sp500",
                                            account_name="agis")
       
    def next(self):
        self.check_positions()
        predicted_returns = {asset_name : self.exchange.get(asset_name, "Next Return") 
                             for asset_name in self.asset_names}
        predicted_returns = {k: v for k, v in predicted_returns.items() if not isnan(v)}
        predicted_returns = {k: v for k, v in sorted(predicted_returns.items(), key=lambda item: item[1], reverse = True)}
        _avg_predicted_return = sum(predicted_returns.values()) / len(predicted_returns)
        
        nlv = self.broker.get_nlv(account_name="agis")
        position_size = (nlv) / (self.position_count * self.lookahead) * .5
        
        keys = list(predicted_returns.keys())
        counts = 0
        if _avg_predicted_return > 0:
            for index, asset_name in enumerate(keys):
                #if self.broker.position_exists(asset_name): continue
                market_price = self.exchange.get_market_price(asset_name)
                units = position_size / market_price
                self.broker.place_market_order(asset_name, units,
                                            strategy_id=self.strategy_id,
                                            account_name="agis",
                                            exchange_name="sp500")
                counts += 1
                if counts == self.position_count: break
        
        counts = 0
        if _avg_predicted_return < 0: 
            for index, asset_name in enumerate(keys[::-1]):
                #if self.broker.position_exists(asset_name): continue
                market_price = self.exchange.get_market_price(asset_name)
                units = -1 * (position_size / market_price)
                self.broker.place_market_order(asset_name, units,
                                            strategy_id=self.strategy_id,
                                            account_name="agis",
                                            exchange_name="sp500")
                counts += 1
                if counts == self.position_count: break
           
    def load(self):
        z = zipfile.ZipFile(self.zip_path)
        file_names = z.namelist()
        asset_names = [_file[0:-4] for _file in file_names]
        
        _file = file_names[0]
        self.count = 0
        for index, _file in enumerate(file_names):
            f = z.open(_file)
            file_string = io.StringIO(f.read().decode("utf-8"))
            
            df = pd.read_csv(file_string, sep=",")
            df["DATE"] = pd.to_datetime(pd.to_datetime(df["DATE"], format = "%Y-%m-%d"))
            df.set_index("DATE",inplace=True)
            
            asset_name = asset_names[index]
            new_asset = self.ft.register_asset(asset_name, "sp500")
            new_asset.set_format("%d-%d-%d", 0, 1)
            new_asset.load_from_df(df, nano=True)
            self.count += df.shape[0]
            
    def load_benchmark(self):            
        df = pd.read_csv("/Users/nathantormaschy/Downloads/SPY.csv")
        df["DATE"] = pd.to_datetime(df["DATE"], format = "%Y-%m-%d")
        df["DATE"] = df['DATE'].apply(lambda x: x.replace(tzinfo=None))
        df["DATE"] = pd.to_datetime(df["DATE"])
        df.set_index("DATE",inplace=True)
        return df
                
if __name__ == "__main__":

    ft = FastTest(logging=False, debug=False, save_last_positions=True)
    
    exchange = Exchange(exchange_name="sp500")
    ft.register_exchange(exchange)
    
    broker = Broker(exchange, margin=True, logging=False)
    ft.register_broker(broker)
    ft.add_account("agis", 100000)
    
    strategy = Agis_Strategy(broker, exchange, ft, lookahead=20)
    
    exchange.set_slippage(.0025)
    
    benchmark = Asset(exchange.exchange_id, asset_name=str("Benchmark"))
    ft.register_benchmark(benchmark)
    benchmark.set_format("%d-%d-%d", 0, 1)
    benchmark.load_from_df(strategy.load_benchmark(), nano=True)

    ft.add_strategy(strategy)
    ft.build()
    
    st = time.time()
    ft.run()
    et = time.time()
    
    print(strategy.count / (et-st))
    #print(ft.metrics.get_stats())
    
    #last_positions = ft.get_last_positions(to_df=True)
    ft.plot(benchmark.df())
