import pandas as pd
import numpy as np
import time

from Order import *
from Asset import Asset

class Exchange():
    def __init__(self) -> None:
        self.asset_count = 0
        self.datetime_idx = 0
        self.market = {}
        self.market_view = {}
        self.orders = []

    def register_asset(self, asset : Asset) -> None:
        self.market[asset.asset_name] = asset
        self.asset_count += 1

    def remove_asset(self, asset_name : str) -> None:
        del self.market[asset_name]

    def build_market_view(self):
        self.market_view = {}
        try:
            current_time = self.datetime_index[self.datetime_idx]
        except IndexError:
            return False
        self.market_view["current_datetime"] = current_time
        self.market_time = current_time
        for asset in self.market.values():
            asset_view = asset.get_asset_view(current_time)
            if asset_view: self.market_view[asset.asset_name] = asset_view
        self.datetime_idx += 1
        return True

    def next(self) -> bool:
        market_view = self.build_market_view()
        return market_view

    def build(self) -> None:
        if len(self.market.keys()) == 0: raise RuntimeError("attempting to build exchange with no assets registered")
        datetime_index_list = [asset.df.index for asset in self.market.values()]
        self.datetime_index = pd.DatetimeIndex(np.unique(np.hstack(datetime_index_list)))

    def handle_market_order(self, order : Order):
        market_price = self.market_view[order.asset_name]["OPEN"]
        self.order.fill(self.market_time,market_price)

    def place_orders(self, orders):
        self.orders += orders

    def process_orders(self):
        orders_filled = []
        for order in self.orders:
            if order.order_type.value == 1:
                self.handle_market_order(order)
                if order.order_state == OrderState.FILLED:
                    orders_filled.append(order)
                    
        return orders_filled

if __name__ == "__main__":

    exchange = Exchange()

    source_type = "csv"
    datetime_format = "%Y-%m-%d"
    datetime_column = "DATE"

    tickers = ["A","AAL","AAP","AAPL"]

    for ticker in tickers:
        csv_path = r"C:\Users\bktor\Desktop\Python\FastTest\data\{}.csv".format(ticker)
        name = ticker
        exchange.register_asset(Asset(
                ticker,
                source_type = source_type,
                csv_path = csv_path,
                datetime_format = datetime_format,
                datetime_column = datetime_column
            )
        )
    exchange.build()
    exchange.run()