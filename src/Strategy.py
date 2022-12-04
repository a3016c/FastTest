
from Exchange import Exchange
from Broker import Broker
from Order import *

class Strategy():
    def __init__(self, exchange : Exchange, broker : Broker) -> None:
        self.exchange = exchange
        self.broker = broker

    def next(self, filled_orders):
        return []
