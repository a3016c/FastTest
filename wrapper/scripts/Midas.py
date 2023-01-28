import sys
import os
import pandas as pd
from math import isnan, floor

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import numpy as np
from Exchange import Exchange
from Broker import Broker
from Strategy import Strategy
from FastTest import FastTest
import math

class Midas_Strategy(Strategy):
    def __init__(self, broker: Broker, exchange: Exchange, ft : FastTest, asset_name : str, cash : float) -> None:
        super().__init__(broker, exchange)
        self.ft = ft
        self.lookahead = 5
        self.asset_name = asset_name
        self.starting_cash = cash
        self.load()
        
    def next(self):
        predicted_returns = self.exchange.get(self.asset_name,"LR_PREDS")
        
        position_size = .9*self.starting_cash

        if not self.broker.position_exists(self.asset_name,
                                        exchange_name=self.exchange.exchange_name,
                                        account_id = -1):
            
            market_price = self.exchange.get_market_price(self.asset_name)
            
            if math.isnan(market_price):
                return

            units = abs(position_size / market_price)
            if predicted_returns < .5:
                units *= -1
            self.broker.place_market_order(self.asset_name, units,
                                        exchange_name=self.exchange.exchange_name,
                                        account_name="midas",
                                        strategy_id=self.strategy_id)
            return 
        
        position = self.broker.get_position(self.asset_name,
                                        account_name="midas",
                                        exchange_name=self.exchange.exchange_name)
        
        if predicted_returns < 0.5 and position.units < 0:
            return
        elif predicted_returns > 0.5 and position.units > 0:
            return
        else:
            units = -1 * position.units
            self.broker.place_market_order(self.asset_name, units,
                                        strategy_id=self.strategy_id,
                                        exchange_name=self.exchange.exchange_name,
                                        account_name="midas")
            return
        
    def load(self):
        df = pd.read_csv("/Users/nathantormaschy/Downloads/df_sub.csv")
        df["DATE"] = pd.to_datetime(df["DATE"], format = "%Y-%m-%d")
        df["DATE"] = df['DATE'].apply(lambda x: x.replace(tzinfo=None))
        df["DATE"] = pd.to_datetime(df["DATE"])
        df.set_index("DATE",inplace=True)
        new_asset = self.ft.register_asset("SPY", "SPY")
        new_asset.set_format("%d-%d-%d", 0, 0)
        new_asset.load_from_df(df, nano=True)
        
    def load_benchmark(self):            
        df = pd.read_csv("/Users/nathantormaschy/Downloads/SPY.csv")
        df["DATE"] = pd.to_datetime(df["DATE"], format = "%Y-%m-%d")
        df["DATE"] = df['DATE'].apply(lambda x: x.replace(tzinfo=None))
        df["DATE"] = pd.to_datetime(df["DATE"])
        df.set_index("DATE",inplace=True)
        return df
        
if __name__ == "__main__":
    ft = FastTest(logging=False, debug=False)
    spy_exchange = Exchange(exchange_name="SPY")
    ft.register_exchange(spy_exchange)
    
    broker = Broker(spy_exchange, margin=True, logging=False)
    ft.register_broker(broker)
    ft.add_account("midas", 100000)
    
    midas_strategy = Midas_Strategy(broker, spy_exchange, ft, "SPY", 100000)
    
    ft.add_strategy(midas_strategy)
    
    ft.build()
    ft.run()
    
    ft.plot()
