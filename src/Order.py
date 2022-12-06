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
        self.order_create_time = kwargs["order_create_time"]
        self.asset_name = kwargs["asset_name"]
        self.units = kwargs["units"]

    def set_order_id(self, order_id : int):
        self.order_id = order_id

    def fill(self, order_fill_time : datetime64, fill_price : float):
        self.order_state = OrderState.FILLED
        self.fill_price = fill_price

    def cancel(self, order_cancel_time : datetime64):
        self.order_state = OrderState.CANCLED

class MarketOrder(Order):
    def __init__(self, **kwargs) -> None:
        super().__init__(OrderType.MARKET_ORDER,
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

        
        