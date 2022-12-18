from Broker import *
from ctypes import *
import sys 
import LibWrapper
from Exchange import Exchange
from Order import OrderSchedule, OrderType

class Strategy():
    def __init__(self, broker = None, exchange = None) -> None:
        self.broker = broker
        self.exchange = None

    def build(self, broker, exchange) -> None:
        self.broker = broker
        self.exchange = exchange
        self.broker_ptr = broker.ptr
        self.exchange_ptr = exchange.ptr

    def get(self, asset_name : str, feature_name : str):
        return LibWrapper._get_market_feature(
            self.exchange_ptr,
            c_char_p(asset_name.encode("utf-8")),
            c_char_p(feature_name.encode("utf-8")),
        )

    def next():
        return 

class TestStrategy(Strategy):
    def __init__(self, order_schedule, broker = None, exchange = None) -> None:
        super().__init__(broker,exchange)
        self.order_schedule = order_schedule
        self.i = 0

    def next(self):
        for order in self.order_schedule:
            if order.i == self.i:
                if order.order_type == OrderType.MARKET_ORDER:
                    self.broker.place_market_order(order.asset_name,order.units,order.cheat_on_close)
                elif order.order_type == OrderType.LIMIT_ORDER:
                    self.broker.place_market_order(order.asset_name,order.units,order.limit,order.cheat_on_close)

        self.i += 1
        
class BenchMarkStrategy(Strategy):
    def __init__(self, broker = None, exchange = None) -> None:
        super().__init__(broker,exchange)
        self.i = 0

    def next(self):
        if self.i == 0:
            number_assets = self.exchange.asset_count()
            asset_names = self.exchange.asset_names
            for i in range(0,number_assets):
                res = self.broker.place_market_order(asset_names[i],100)
            print(res)
            self.i += 1