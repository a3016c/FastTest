import numpy as np
import pandas as pd
import os 
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
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

file_name_1 = r"/Users/nathantormaschy/Desktop/C++/FastTest/wrapper/tests/data/test1.csv"
file_name_2 = r"/Users/nathantormaschy/Desktop/C++/FastTest/wrapper/tests/data/test2.csv"

def get_unix_time(dt64):
    return dt64.astype("datetime64[s]").astype('int')

df1 = pd.DataFrame(index = get_unix_time(test1_index),data = np.vstack((test1_open,test1_close)).T, columns=["OPEN","CLOSE"])
df2 = pd.DataFrame(index = get_unix_time(test2_index),data = np.vstack((test2_open,test2_close)).T, columns=["OPEN","CLOSE"])

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

def setup_multi(logging = False):
    exchange = Exchange()
    broker = Broker(exchange)
    ft = FastTest(exchange, broker, logging)

    for i, file_name in enumerate([file_name_1,file_name_2]):
        new_asset = Asset(exchange, asset_name=str(i+1))
        new_asset.set_format("%d-%d-%d", 0, 1)
        new_asset.load_from_csv(file_name)
        ft.exchange.register_asset(new_asset)

    ft.build()
    return exchange, broker, ft


