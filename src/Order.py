from enum import Enum
from numpy import datetime64

class OrderState(Enum):
    OPEN = 1
    FILLED = 2
    ON_FILL = 3
    CANCLED = 4

class OrderType(Enum):
    MARKET_ORDER = 1

class Order():
    def __init__(self, order_type : OrderType, **kwargs) -> None:
        self.order_type = order_type
        self.order_state = OrderState.OPEN
        self.order_id = kwargs["order_id"]
        self.order_create_time = kwargs["order_create_time"]
        self.asset_name = kwargs["asset_name"]
        self.units = kwargs["units"]

        if type(self.order_id) != int: raise TypeError("invalid order id passed to order")
        if type(self.units) != int and type(self.units) != float: raise TypeError("invalid units passed to order")
        if type(self.order_create_time) != datetime64: raise TypeError("invalid order create time passed to order")

    def fill(self, order_fill_time : datetime64, fill_price : float):
        self.order_state = OrderState.FILLED
        self.fill_price = fill_price

class MarketOrder(Order):
    def __init__(self, **kwargs) -> None:
        super().__init__(OrderType.MARKET_ORDER,
            order_id = kwargs['order_id'],
            order_create_time = kwargs['order_create_time'],
            asset_name = kwargs['asset_name'],
            units = kwargs['units']
        )

if __name__ == "__main__":
    order = MarketOrder(
        order_id = 1,
        order_create_time = datetime64('now'),
        asset_name = "AAPL",
        units = 100
    )

        
        