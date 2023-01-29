import numpy as np
import pandas as pd
import os 
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from Exchange import Exchange, Asset
from Account import Account
from Broker import Broker 
from FastTest import FastTest

test1_index = np.array([np.datetime64("2000-06-06T00:00:00"),np.datetime64("2000-06-07T00:00:00"),np.datetime64("2000-06-08T00:00:00"),np.datetime64("2000-06-09T00:00:00")])
test2_index = np.array([np.datetime64("2000-06-05T00:00:00"), np.datetime64("2000-06-06T00:00:00"),np.datetime64("2000-06-07T00:00:00"),
                            np.datetime64("2000-06-08T00:00:00"),np.datetime64("2000-06-09T00:00:00"),np.datetime64("2000-06-12T00:00:00")])

test1_open = np.array([100,102,104,105])
test1_close = np.array([101,103,105,106])
test2_open = np.array([101,100,98,101,101,103])
test2_close = np.array([101.5,99,97,101.5,101.5,96])

file_name_1 = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)),"tests","data","test1.csv")
file_name_2 = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)),"tests","data","test2.csv")

def get_unix_time(dt64):
    return dt64.astype("datetime64[s]").astype('int')

df1 = pd.DataFrame(index = get_unix_time(test1_index),data = np.vstack((test1_open,test1_close)).T, columns=["OPEN","CLOSE"])
df2 = pd.DataFrame(index = get_unix_time(test2_index),data = np.vstack((test2_open,test2_close)).T, columns=["OPEN","CLOSE"])

def setup_simple(logging = False):
    ft = FastTest(logging=logging)
    exchange = Exchange(logging=logging)
        
    ft.register_exchange(exchange)
    broker = Broker(exchange)
    ft.register_broker(broker)
    ft.add_account("default", 100000)

    new_asset = ft.register_asset(asset_name="1")
    new_asset.set_format("%d-%d-%d", 0, 1)
    new_asset.load_from_csv(file_name_2)
    
    ft.build()
    return exchange, broker, ft

def setup_multi(logging = False, margin = False, debug = False):
    
    ft = FastTest(logging=logging, debug=debug)
    exchange = Exchange(logging = logging)
    ft.register_exchange(exchange)
    
    broker = Broker(exchange,logging=logging, margin=margin, debug=debug)
    ft.register_broker(broker)
    ft.add_account("default", 100000)

    for i, file_name in enumerate([file_name_1,file_name_2]):
        new_asset = ft.register_asset(str(i+1))
        new_asset.set_format("%d-%d-%d", 0, 1)
        new_asset.load_from_csv(file_name)
        
    ft.build()
    
    return exchange, broker, ft

def setup_multi_exchange(logging = False, margin = False, debug = False, build = True):
    exchange1 = Exchange(exchange_name="exchange1", logging = logging)
    exchange2 = Exchange(exchange_name="exchange2", logging=logging)
    ft = FastTest(logging, debug)
    
    ft.register_exchange(exchange1) 
    ft.register_exchange(exchange2)
    
    broker = Broker(exchange1,logging=logging, margin=margin)
    ft.register_broker(broker)
    ft.add_account("default", 100000)

    new_asset1 = ft.register_asset("1", "exchange1")
    new_asset2 = ft.register_asset("2", "exchange2")

    new_asset1.set_format("%d-%d-%d", 0, 1)
    new_asset1.load_from_csv(file_name_1)
    
    new_asset2.set_format("%d-%d-%d", 0, 1)
    new_asset2.load_from_csv(file_name_2)
   
    broker.register_exchange(exchange2)
    
    if build: ft.build()
        
    return broker, ft

def setup_multi_account(logging = False, margin = False, debug = False, save_last_positions = True):
    ft = FastTest(logging=logging, debug=debug, save_last_positions=save_last_positions)
    exchange = Exchange(logging = logging)
    ft.register_exchange(exchange)
    
    broker = Broker(exchange,logging=logging, margin=margin, debug=debug)
    ft.register_broker(broker)
    ft.add_account("account1", 100000)
    ft.add_account("account2", 100000)
        
    for i, file_name in enumerate([file_name_1,file_name_2]):
        new_asset = ft.register_asset(str(i+1))
        new_asset.set_format("%d-%d-%d", 0, 1)
        new_asset.load_from_csv(file_name)
        
    ft.build()
    
    return exchange, broker, ft