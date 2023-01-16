import numpy as np
import pandas as pd
import os 
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from Exchange import Exchange, Asset
from Broker import Broker 
from FastTest import FastTest

test1_index = np.array([np.datetime64("2000-06-06T00:00:00"),np.datetime64("2000-06-07T00:00:00"),np.datetime64("2000-06-08T00:00:00"),np.datetime64("2000-06-09T00:00:00")])
test2_index = np.array([np.datetime64("2000-06-05T00:00:00"), np.datetime64("2000-06-06T00:00:00"),np.datetime64("2000-06-07T00:00:00"),
                            np.datetime64("2000-06-08T00:00:00"),np.datetime64("2000-06-09T00:00:00"),np.datetime64("2000-06-12T00:00:00")])

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

def setup_simple(logging = False):
    exchange = Exchange(logging=logging)
    broker = Broker(exchange)
    ft = FastTest(broker, logging=logging)
    
    ft.register_exchange(exchange)

    new_asset = Asset(exchange, asset_name="1")
    new_asset.set_format("%d-%d-%d", 0, 1)
    new_asset.load_from_csv(file_name_2)
    
    exchange.register_asset(new_asset)
    

    ft.build()
    return exchange, broker, ft

def setup_multi(logging = False, margin = False, debug = False):
    exchange = Exchange(logging = logging)
    broker = Broker(exchange,logging=logging, margin=margin, debug=debug)
    ft = FastTest(broker, logging=logging, debug=debug)
    
    ft.register_exchange(exchange)

    for i, file_name in enumerate([file_name_1,file_name_2]):
        new_asset = Asset(exchange, asset_name=str(i+1))
        new_asset.set_format("%d-%d-%d", 0, 1)
        new_asset.load_from_csv(file_name)
        exchange.register_asset(new_asset)
        
    ft.build()
    
    return exchange, broker, ft

def setup_multi_exchange(logging = False, margin = False, debug = False):
    exchange1 = Exchange(exchange_name="exchange1", logging = logging)
    exchange2 = Exchange(exchange_name="exchange2", logging=logging)
    broker = Broker(exchange1,logging=logging, margin=margin)
    ft = FastTest(broker, logging, debug)
    
    ft.register_exchange(exchange1) 
    ft.register_exchange(exchange2)

    new_asset1 = Asset(exchange1, asset_name=str(1))
    new_asset2 = Asset(exchange2, asset_name=str(2))

    new_asset1.set_format("%d-%d-%d", 0, 1)
    new_asset1.load_from_csv(file_name_1)
    
    new_asset2.set_format("%d-%d-%d", 0, 1)
    new_asset2.load_from_csv(file_name_2)
    
    exchange1.register_asset(new_asset1)
    exchange2.register_asset(new_asset2)
       

    broker.register_exchange(exchange2)
    
    ft.build()
        
    return broker, ft




