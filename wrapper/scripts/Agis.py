import sys
import os
import time
import unittest
import zipfile
import io
from math import isnan, floor

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import numpy as np
from Exchange import Exchange, Asset
from Broker import Broker
from Strategy import *
from FastTest import FastTest
import Wrapper

class Agis_Strategy(Strategy):
    def __init__(self, broker: Broker, exchange: Exchange) -> None:
        super().__init__(broker, exchange)
        self.zip_path = "/Users/nathantormaschy/Downloads/preds_test.zip"
        self.load()
        self.i = 0
        self.lookahead = 20
        self.position_size = .025
        self.position_count = 2
        
    def check_positions(self):
        positions = self.broker.get_positions()
        for i in range(positions.number_positions):
            position = positions.POSITION_ARRAY[i].contents
            if position.bars_held == self.lookahead:
                asset_name = self.exchange.id_map[position.asset_id]
                self.broker.place_market_order(asset_name, -1*position.units)
                
    def close_positions(self):
        positions = self.broker.get_positions()
        for i in range(positions.number_positions):
            position = positions.POSITION_ARRAY[i].contents
            asset_name = self.exchange.id_map[position.asset_id]
            self.broker.place_market_order(asset_name, -1*position.units)
        
    def build(self):
        self.asset_names = self.exchange.id_map.values()
        
    def next(self):
        self.check_positions()
        predicted_returns = {asset_name : self.exchange.get(asset_name, "Next Return") 
                             for asset_name in self.asset_names if not isnan(self.exchange.get(asset_name, "Next Return"))}
        predicted_returns = {k: v for k, v in sorted(predicted_returns.items(), key=lambda item: item[1], reverse = True)}
        _avg_predicted_return = sum(predicted_returns.values()) / len(predicted_returns)
        
        #if _avg_predicted_return <= 0:
            #self.close_positions()
            #return
        
        nlv = broker.get_nlv()
        position_size = (nlv) / (self.position_count * self.lookahead) * .95
     
        keys = list(predicted_returns.keys())
        counts = 0
        if _avg_predicted_return > 0:
            for index, asset_name in enumerate(keys):
                #if self.broker.position_exists(asset_name): continue
                market_price = self.exchange.get_market_price(asset_name)
                units = position_size / market_price
                self.broker.place_market_order(asset_name, units)
                counts += 1
                if counts == self.position_count: break
        
        counts = 0
        if _avg_predicted_return < 0: 
            for index, asset_name in enumerate(keys[::-1]):
                #if self.broker.position_exists(asset_name): continue
                market_price = self.exchange.get_market_price(asset_name)
                units = -1 * (position_size / market_price)
                self.broker.place_market_order(asset_name, units)
                counts += 1
                if counts == self.position_count: break
           
    def load(self):
        z = zipfile.ZipFile(self.zip_path)
        file_names = z.namelist()
        asset_names = [_file[0:-4] for _file in file_names]
        
        _file = file_names[0]
        
        for index, _file in enumerate(file_names):
            f = z.open(_file)
            file_string = io.StringIO(f.read().decode("utf-8"))
            
            df = pd.read_csv(file_string, sep=",")
            df["DATE"] = pd.to_datetime(pd.to_datetime(df["DATE"], format = "%Y-%m-%d"))
            df.set_index("DATE",inplace=True)
            
            asset_name = asset_names[index]
            new_asset = Asset(exchange, asset_name=asset_name)
            new_asset.set_format("%d-%d-%d", 0, 1)
            new_asset.load_from_df(df, nano=True)
            ft.exchange.register_asset(new_asset)
                
if __name__ == "__main__":

    exchange = Exchange()
    broker = Broker(exchange)
    ft = FastTest(exchange, broker, False)
    
    strategy = Agis_Strategy(broker, exchange)
    
    ft.build()

    df = pd.read_csv("/Users/nathantormaschy/Downloads/SPY.csv")
    df["Date"] = pd.to_datetime(pd.to_datetime(df["Date"], format = "%Y-%m-%d"))
    df.set_index("Date",inplace=True)
    
    benchmark = Asset(exchange, asset_name=str("Benchmark"))
    benchmark.set_format("%d-%d-%d", 0, 1)
    benchmark.load_from_df(df, nano=True)
    ft.register_benchmark(benchmark)

    ft.add_strategy(strategy)
    ft.run()

    positions = broker.get_position_history().to_df()
    positions["asset_id"] = positions["asset_id"].map(exchange.id_map)
    print(positions)
    strategy.plot(benchmark)

    
