import pandas as pd 
import numpy as np

from Strategy import Strategy
from Exchange import Exchange
from Broker import Broker
from Asset import Asset
from Order import *


class FastTest():
    def __init__(self, exchange : Exchange, broker : Broker, strategy : Strategy) -> None:
        self.exchange = exchange
        self.broker = broker
        self.strategy = strategy
        self.exchange.build()
        
    def run(self):
        while self.exchange.next():

            #evaluate collateral held by broker
            self.broker.evaluate_collateral()

            #allow exchange to process open orders from previous steps
            filled_orders = self.exchange.process_orders()

            #allow broker to process orders that have been filled
            self.broker.process_filled_orders(filled_orders) 

            #allow strategy to place orders based on current market view. Orders processed next market open
            orders = self.strategy.next(filled_orders = filled_orders)

            #place the orders to the broker who routes them to the exchange
            self.broker.place_orders(orders)

            #value the portfolio
            self.broker.evaluate_portfolio()

        """End of backtest"""

        #clear all orders currently open on the exchange
        self.broker.clear_orders()
        
        #close all open positions at last close price for each asst
        self.broker.clear_portfolio()

        #provide a final valuation of the portfolio
        self.broker.evaluate_portfolio()


if __name__ == "__main__":
    exchange = Exchange()
    broker = Broker(exchange=exchange)
    strategy = Strategy(exchange=exchange,broker=broker)

    source_type = "csv"
    datetime_format = "%Y-%m-%d"
    datetime_column = "DATE"

    tickers = ["AAL","AAP"]

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
    
    fast_test = FastTest(
        exchange=exchange,
        broker=broker,
        strategy=strategy
        )
    
    fast_test.run()