import numpy as np
from Exchange import Exchange, Asset
from Broker import Broker 
from FastTest import FastTest

test1_index = np.array([np.datetime64("2000-06-06T05:00:00"),np.datetime64("2000-06-07T05:00:00"),np.datetime64("2000-06-08T05:00:00"),np.datetime64("2000-06-09T05:00:00")])
test2_index = np.array([np.datetime64("2000-06-05T05:00:00"), np.datetime64("2000-06-06T05:00:00"),np.datetime64("2000-06-07T05:00:00"),
                            np.datetime64("2000-06-08T05:00:00"),np.datetime64("2000-06-09T05:00:00"),np.datetime64("2000-06-12T05:00:00")])

test1_open = np.array([100,102,104,105])
test1_close = np.array([101,103,105,106])
test2_open = np.array([101,100,98,101,101,103])
test2_close = np.array([101.5,99,97,101.5,101.5,96])

file_name_1 = r"C:\Users\bktor\Desktop\Python\FastTest\src\wrapper\tests\data\test1.csv"
file_name_2 = r"C:\Users\bktor\Desktop\Python\FastTest\src\wrapper\tests\data\test2.csv"
file_name_big = r"C:\Users\bktor\test_large.csv"


def setup_simple():
    exchange = Exchange()
    broker = Broker(exchange)
    ft = FastTest(exchange, broker)

    new_asset = Asset(exchange, asset_name="1")
    new_asset.set_format("%d-%d-%d", 0, 1)
    new_asset.load_from_csv(file_name_2)
    ft.exchange.register_asset(new_asset)

    ft.build()
    return exchange, broker, ft

def setup_multi():
    exchange = Exchange()
    broker = Broker(exchange)
    ft = FastTest(exchange, broker)

    for i, file_name in enumerate([file_name_1,file_name_2]):
        new_asset = Asset(exchange, asset_name=str(i+1))
        new_asset.set_format("%d-%d-%d", 0, 1)
        new_asset.load_from_csv(file_name)
        ft.exchange.register_asset(new_asset)

    ft.build()
    return exchange, broker, ft

