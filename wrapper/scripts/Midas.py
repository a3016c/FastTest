import sys
import os
import time
import zipfile
import io
from math import isnan, floor

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import numpy as np
from Exchange import Exchange, Asset
from Broker import Broker
from Strategy import Strategy
from FastTest import FastTest

class Midas_Strategy(Strategy):
    def __init__(self, broker: Broker, exchange: Exchange, asset_name : str,lookahead) -> None:
        super().__init__(broker, exchange)
        self.lookahead = 5
        self.asset_name = asset_name
        
    def next(self):
        predicted_returns = self.exchange.get(self.asset_name,"LR_PREDS")
        
        position_size = 50000

        if not self.broker.position_exists(self.asset_name):
            market_price = self.exchange.get_market_price(self.asset_name)
            units = abs(position_size / market_price)
            if predicted_returns < .5:
                units *= -1
            self.broker.place_market_order(self.asset_name, units, strategy_id=self.strategy_id)
            return 
        
        position = self.broker.get_position(self.asset_name)
        
        if predicted_returns < 0.5 and position.units < 0:
            return
        elif predicted_returns > 0.5 and position.units > 0:
            return
        elif predicted_returns < 0.5 and position.units > 0:
            units = -1 * position.units
            self.broker.place_market_order(self.asset_name, units, strategy_id=self.strategy_id)
            return
        elif predicted_returns > 0.5 and position.units < 0:
            units = -1 * position.units
            self.broker.place_market_order(self.asset_name, units, strategy_id=self.strategy_id)
            return