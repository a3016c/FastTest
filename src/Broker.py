from numpy import timedelta64
from Order import *
from Exchange import Exchange
from Position import Position
import logging
import os

class Broker():
    def __init__(self, exchange : Exchange) -> None:
        self.cash = 100000
        self.portfolio = {}
        self.exchange = exchange
        self.margin_requirement = 1
        self.realized_pl = 0
        self.unrealized_pl = 0
        self.order_counter = 0

        self.cheat_on_close = False

        self.position_history = []
        self.order_history = []

        log_path = "log1.txt"
        try:
            os.remove(log_path)
        except OSError:
            pass
        logging.basicConfig(
            filename=log_path,
            format="%(asctime)s BROKER: %(message)s",
            filemode="w"
        )
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

    def build(self):
        self.strategy_analysis = {
            asset_name : {
            "commision_paid" : 0,
            "time_in_market" : timedelta64(0),
            "total_units" : 0,
            "pl" : 0,
            "number_trades" : 0,
            "wins" : 0,
            "losses" : 0,
            "win_rate" : 0,
            "average_time_in_market" : 0,
            "average_position_size" : 0,
            "average_pl" : 0
            }
            for asset_name in list(self.exchange.market.keys())
        }

    def reset(self):
        self.cash = 100000
        self.portfolio = {}
        self.realized_pl = 0
        self.unrealized_pl = 0

    def evaluate_portfolio(self, market_price_column = "CLOSE"):
        #evaluate each asset in the portfolio using current market prices
        #portfolio evaluation is run at the end of each period
        for keys in list(self.portfolio.keys()):
            position = self.portfolio[keys]
            market_price = self.exchange.market_view[position.asset_name][market_price_column]
            position.evaluate(market_price)
            #if asset runs out of data to stream we have to close the position at the last close pice
            if self.exchange.market[position.asset_name].streaming == False: 
                self.close_position(position.asset_name, market_price, on_open = False)
        self.get_net_liquidation_value()

    def get_net_liquidation_value(self):
        #net liquidation value is sum of cash, long position, and portfolio colateral
        #minus short position values
        self.net_liquidation_value = self.cash + sum([position.liquidation_value() for position in self.portfolio.values()])

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

    def clear_orders(self):
        self.logger.debug("clearing orders from the exchange")
        self.exchange.orders = []

    def clear_portfolio(self, on_open = False):
        self.logger.debug(f"datetime: {self.exchange.market_time}, clearing portfolio")
        for asset_name in list(self.portfolio.keys()):
            asset = self.portfolio[asset_name]
            market_price = self.exchange.market_view[asset.asset_name]["CLOSE"]
            self.close_position(asset.asset_name,market_price,on_open=on_open)

    def open_position(self, asset_name : str, market_price : float, units : float, **kwargs):
        self.logger.debug(
            f"datetime: {self.exchange.market_time}, "
            f"opening new position in {asset_name}, "
            f"market_price: {market_price}, units: {units}"
        )
        collateral = market_price * abs(units) * self.margin_requirement
        new_position = Position(
            asset_name = asset_name,
            average_price = market_price,
            units = units,
            position_open_time = self.exchange.market_time,
            margin_requirement = self.margin_requirement,
            collateral = collateral
        )
        self.portfolio[asset_name] = new_position
        self.cash -= collateral
        #for short sales we credit the account cash recieved from selling the borrowed shares
        if units < 0: self.cash += abs(units) * market_price

    def close_position(self, asset_name : str, market_price : float, on_open = True, **kwargs):
        self.logger.debug(
            f"datetime: {self.exchange.market_time}, "
            f"closing existing position in {asset_name}, "
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

        #analyze position and add to history 
        self.position_history.append(existing_position)
        strategy_analysis_asset = self.strategy_analysis[existing_position.asset_name]
        strategy_analysis_asset["pl"] += existing_position.realized_pl
        strategy_analysis_asset["total_units"] += abs(existing_position.units)
        
        bars_index = self.exchange.market[asset_name].df.index
        bars_held = bars_index.get_loc(existing_position.position_close_time) - bars_index.get_loc(existing_position.position_open_time)
        strategy_analysis_asset["time_in_market"] += bars_held * self.exchange.market[asset_name].timedelta

        #if position was closed on open, subrtract one time period to reflect that in the time_in_market
        if on_open: strategy_analysis_asset["time_in_market"] -= self.exchange.market[asset_name].timedelta
        #if we cheat and buy on close we have to add in one period to reflect that in the time_in_market
        if not self.cheat_on_close: strategy_analysis_asset["time_in_market"] += self.exchange.market[asset_name].timedelta

        if existing_position.realized_pl > 0: strategy_analysis_asset["wins"] += 1
        else : strategy_analysis_asset["losses"] += 1
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

    def place_orders(self, orders, strategy_id : str):
        if orders == None: return 
        for i in range(len(orders)):
            orders[i].set_order_id(self.order_counter)
            orders[i].strategy_id = strategy_id
            self.order_counter += 1
        self.order_history += orders
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
                