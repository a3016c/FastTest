
from Order import *
from Exchange import Exchange
from Position import Position
import logging

class Broker():
    def __init__(self, exchange : Exchange) -> None:
        self.cash = 100000
        self.portfolio = {}
        self.exchange = exchange
        self.margin_requirement = 1
        self.realized_pl = 0
        self.unrealized_pl = 0
        
        logging.basicConfig(
            filename=r"tests\logs\log1.txt",
            format="%(asctime)s BROKER: %(message)s",
            filemode="w"
        )
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

    def evaluate_portfolio(self, market_price_column = "CLOSE"):
        #evaluate each asset in the portfolio using current market prices
        #portfolio evaluation is run at the end of each period
        for asset in self.portfolio.values():
            market_price = self.exchange.market_view[asset.asset_name][market_price_column]
            asset.evaluate(market_price)

    def evaluate_collateral(self, market_price_column = "OPEN"):
        #adjust collateral requirments for stocks sold short
        #adjustment evaluation is run at the beginning of each period
        margin_adjustment = 0
        for asset in self.portfolio.values():
            if asset.units > 0: continue 
            market_price = self.exchange.market_view[asset.asset_name][market_price_column]
            margin_adjustment += asset.collateral_adjustment(market_price)
        self.cash -= margin_adjustment
        if self.cash < 0: raise RuntimeError("margin call issued, collateral can not be posted from cash")

    def net_liquidation_value(self):
        #net liquidation value is sum of cash, long position, and portfolio colateral
        #minus short position values
        return self.cash + sum([position.liquidation_value() for position in self.portfolio.values()])
    
    def clear_orders(self):
        self.logger.debug("clearing orders from the exchange")
        del self.exchange.orders

    def clear_portfolio(self):
        self.logger.debug(f"datetime: {self.exchange.market_time}, clearing portfolio")
        for asset in self.portfolio.values():
            market_price = market_price = self.exchange.market_view[asset.asset_name]["CLOSE"]
            self.close_position(asset.asset_name,market_price)

    def open_position(self, asset_name : str, market_price : float, units : float, **kwargs):
        self.logger.debug(
            f"datetime: {self.exchange.market_time},"
            f"opening new position in {asset_name},"
            f"market_price: {market_price}, units: {units}, "
        )
        collateral = market_price * abs(units) * self.margin_requirement
        new_position = Position(
            asset_name = asset_name,
            units = units,
            position_open_time = self.exchange.market_time,
            margin_requirement = kwargs.get("margin_rate"),
            collateral = collateral
        )
        self.portfolio[asset_name] = new_position
        self.cash -= collateral
        #for short sales we credit the account cash recieved from selling the borrowed shares
        if units < 0: self.cash += abs(units) * market_price

    def close_position(self, asset_name : str, market_price : float, **kwargs):
        self.logger.debug(
            f"datetime: {self.exchange.market_time},"
            f"closing existing position in {asset_name},"
            f"market_price: {market_price} "
        )
        existing_position = self.portfolio.get(asset_name)
        if existing_position == None: raise KeyError("attempted to close position that does not exist")
        existing_position.close(market_price, self.exchange.market_time)
        
        if existing_position.units > 0:
            #for long positions account is credited with the sale value
            self.cash += existing_position.units * market_price
        else:
            #short positions must buy back stock at market price
            self.cash -= abs(existing_position.units) * market_price
            #release collateral held by position as well as gain from transaction
            self.cash += existing_position.collateral + self.realized_pl

        del self.portfolio[asset_name]

    def increase_position(self, asset_name : str, units : float, market_price : float,**kwargs):
        self.logger.debug(
            f"datetime: {self.exchange.market_time},"
            f"increasing existing position in {asset_name},"
            f"market_price: {market_price}, units: {units}"
        )
        existing_position = self.portfolio.get(asset_name)
        if existing_position == None: raise KeyError("attempted to increase position that does not exist")
        if (existing_position.units * units) < 0: raise RuntimeError("attempting to increase position with opposite signed units")
        
        existing_position.increase(units, market_price)
        if existing_position.units > 0:
            #reduce cash in account by long position value
            self.cash -= units * market_price
        else:
            #post additional short sale collateral
            self.cash -= abs(units) * market_price * self.margin_requirement
            #recieve cash from short sale of shares
            self.cash += abs(units) * market_price

    def reduce_position(self, asset_name : str, units : float, market_price : float):
        self.logger.debug(
            f"datetime: {self.exchange.market_time},"
            f"reducing existing position in {asset_name},"
            f"market_price: {market_price}, units: {units}"
        )
        existing_position = self.portfolio.get(asset_name)
        if existing_position == None: raise KeyError("attempted to reduce position that does not exist")
        if (existing_position.units * units) > 0: raise RuntimeError("attempting to reduce position with same signed units")
        
        existing_position.reduce(units, market_price)
        if existing_position.units > 0:
            #reflect cash recieved from reduction of long position
            self.cash -= units  * market_price
        else:
            #release collateral held against borrow shares bough back
            self.cash += abs(units) * market_price * self.margin_requirement
            #reduce cash required to buy back shares
            self.cash -= abs(units) * market_price

    def place_orders(self, orders):
        self.exchange.place_orders(orders)

    def process_filled_orders(self, orders):
        for order in orders:
            asset_name = order.asset_name
            units = order.units
            fill_price =  order.fill_price
            existing_position = self.portfolio.get(asset_name)
            if existing_position == None:
                self.open_position(asset_name,fill_price,units)
            else:
                if units + existing_position.units == 0:
                    self.close_position(asset_name,fill_price)
                elif units * existing_position.units > 0:
                    self.increase_position(asset_name,units,fill_price)
                else:
                    self.reduce_position(asset_name,units,fill_price)
                