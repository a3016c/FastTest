from enum import Enum
from numpy import datetime64

class PositionState(Enum):
    OPEN = 1
    CLOSED = 2

class Position():
    def __init__(self, asset_name : str, **kwargs) -> None:
        self.position_state = PositionState.OPEN
        self.asset_name = asset_name
        self.average_price = kwargs["average_price"]
        self.last_price = kwargs["average_price"]
        self.units = kwargs["units"]
        self.position_open_time = kwargs["position_open_time"]
        self.position_close_time = None
        self.bars_held = 0
        self.margin_requirement = kwargs.get("margin_requirement")
        self.collateral = kwargs.get("collateral")
        self.unrealized_pl = 0
        self.realized_pl = 0
        self.commision_paid = 0

    def __repr__(self) -> str:
        return (
            f"asset_name: {self.asset_name}, "
            f"average_price: {self.average_price}, "
            f"close_price: {self.close_price}, "
            f"units: {self.units}, "
            f"position_open_time: {self.position_open_time}, "
            f"position_close_time: {self.position_close_time}, "
            f"unrealized_pl: {self.unrealized_pl}, "
            f"realized_pl: {self.realized_pl}"
        )

    def evaluate(self, market_price : float):
        self.last_price = market_price
        self.unrealized_pl = self.units * (market_price - self.average_price)

    def liquidation_value(self):
        if self.units > 0 and self.margin_requirement == 1: return self.units * self.last_price
        else: raise NotImplemented("short position evaluation not implemented")

    def collateral_adjustment(self, market_price : float):
        if self.units > 0: return 0
        margin_requirment = abs(self.units) * market_price * self.margin_requirement
        adjustment = margin_requirment - self.collateral
        self.collateral += adjustment
        return adjustment 

    def increase(self, units : float, market_price : float, **kwargs):
        self.average_price = ((abs(self.units) * self.average_price) + (abs(units) * market_price))/(abs(units) + abs(self.units))
        self.units += units
        if units < 0: 
            self.collateral += abs(units) * market_price * self.margin_requirement

    def reduce(self, units : float, market_price : float, **kwargs):
        self.realized_pl += units * (market_price - self.average_price)
        self.units -= units

    def close(self, close_price : float, position_close_time : datetime64, **kwargs):
        self.position_state = PositionState.CLOSED
        self.close_price = close_price 
        self.position_close_time = position_close_time
        self.evaluate(close_price)
        self.realized_pl += self.unrealized_pl
        self.unrealized_pl = 0

