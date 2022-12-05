
from Exchange import Exchange
from Broker import Broker
from Order import *

class Strategy():
    def __init__(self, exchange : Exchange, broker : Broker) -> None:
        self.exchange = exchange
        self.broker = broker

    def reset(self):
        self.exchange.reset()
        self.broker.rest()

    def next(self):
        return []

class BenchMarkBH(Strategy):
    def __init__(self, exchange: Exchange, asset_name : str) -> None:
        self.broker = Broker(exchange=exchange)
        self.broker.cheat_on_close = True
        super().__init__(exchange, self.broker)
        self.invested = False
        self.asset_name = asset_name

    def next(self):
        if not self.invested:
            new_order = MarketOrder(
                order_create_time = self.exchange.market_time,
                asset_name = self.asset_name,
                units = self.broker.cash / (self.exchange.market_view[self.asset_name]["CLOSE"])
            )
            self.invested = True
            return [new_order]
