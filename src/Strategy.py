
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
