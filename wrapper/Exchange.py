import sys
import os
from ctypes import *

import numpy as np
import pandas as pd

SCRIPT_DIR = os.path.dirname(__file__)
sys.path.append(os.path.dirname(SCRIPT_DIR))

from wrapper import  Wrapper

class Exchange():
    # -----------------------------------------------------------------------------
    def __init__(self, exchange_name = "default", logging = False, debug = False) -> None:
        self.logging = logging
        self.debug = debug
        self.exchange_name = exchange_name
        self.exchange_id = None
        self.ptr = Wrapper._new_exchange_ptr(logging)
        self.asset_map = {}
        self.id_map = {}
        self.asset_counter = 0
        
        if self.debug: print(f"ALLOCATING EXCHANGE POINTER AT {self.ptr}")

    # -----------------------------------------------------------------------------
    def __del__(self):
        #free the allocated exchange pointer
        if self.debug: print(f"\nFREEING {self.exchange_name} EXCHANGE POINTER AT {self.ptr}")
        Wrapper._free_exchange_ptr(self.ptr)
        if self.debug: print(f"{self.exchange_name} EXCHANGE POINTER FREED\n")

    # -----------------------------------------------------------------------------
    def reset(self):
        Wrapper._reset_exchange(self.ptr)
        
    # -----------------------------------------------------------------------------
    def is_registered(self):
        return Wrapper._exchange_is_registered(self.ptr)
    
    # -----------------------------------------------------------------------------
    def set_slippage(self, slippage : float):
        Wrapper._exchange_set_slippage(self.ptr,slippage)
     
    # -----------------------------------------------------------------------------   
    def register_asset(self, asset):
        if self.asset_map.get(asset.asset_name) != None:
            raise Exception("Asset already exists on exchange")
        
        self.asset_map[asset.asset_name] = asset.asset_id
        self.id_map[asset.asset_id] = asset.asset_name
        self.asset_counter += 1
        asset.registered = True
        Wrapper._register_asset(asset.ptr, self.ptr)
      
    # -----------------------------------------------------------------------------  
    def build(self):
        Wrapper._build_exchange(self.ptr)
        
    # -----------------------------------------------------------------------------
    def get_exchange_index_length(self):
        return Wrapper._get_exchange_index_length(self.ptr)
      
    # -----------------------------------------------------------------------------  
    def get_datetime_index(self):
        index_ptr = Wrapper._get_exchange_datetime_index(self.ptr)
        length = self.get_exchange_index_length()
        return np.ctypeslib.as_array(index_ptr, shape=(length,))
    
    # -----------------------------------------------------------------------------
    def get_asset_name(self, asset_id):
        return self.id_map[asset_id]

    # -----------------------------------------------------------------------------
    def get_market_price(self, asset_name : str, on_close = True):
        asset_id = self.asset_map[asset_name]
        return Wrapper._get_market_price(
            self.ptr, 
            asset_id,
            c_bool(on_close)
        )
       
    # ----------------------------------------------------------------------------- 
    def get(self, asset_name : str, column : str, index = 0):
        asset_id = self.asset_map[asset_name]
        return Wrapper._get_market_feature(
            self.ptr, 
            asset_id,
            c_char_p(column.encode("utf-8")),
            index
        )
       
    # ----------------------------------------------------------------------------- 
    def get_id_max(self, column : str, count : int, max = True):
        ids = (c_uint * count)()
        Wrapper._get_id_max_market_feature(
            self.ptr,
            c_char_p(column.encode("utf-8")),
            cast(ids,POINTER(c_uint)),
            count,
            max
        )
        ids = np.ctypeslib.as_array(ids, shape=(count,))
        return ids
       
    # ----------------------------------------------------------------------------- 
    def get_asset_data(self, asset_name : str):
        asset_id = self.asset_map[asset_name]
        asset_ptr = Wrapper._get_asset_ptr(self.ptr,asset_id)
        return Asset._data(asset_ptr)
     
    # -----------------------------------------------------------------------------   
    def get_market_view(self):
        Wrapper._get_market_view(self.ptr)

    # -----------------------------------------------------------------------------
    def asset_count(self):
        return Wrapper._asset_count(self.ptr)

class Asset():
    # -----------------------------------------------------------------------------
    def __init__(self, exchange_id, asset_name : str,
                exchange_name = None,
                debug = False) -> None:
        self.debug = debug
        self.asset_name = asset_name
        self.registered = False
        self.formatted = False
        self.asset_id = None
        self.exchange_id = exchange_id
        self.exchange_name = exchange_name
        
    # -----------------------------------------------------------------------------
    def load_ptr(self):
        if self.asset_id == None:
            raise RuntimeError("Asset doest not have and ID")
        self.ptr = Wrapper._new_asset_ptr(self.asset_id, self.exchange_id)
        if self.debug: print(f"ALLOCATING {self.asset_name} ASSET POINTER AT {self.ptr}")
        
    # -----------------------------------------------------------------------------
    def __del__(self):
        #free the allocated asset pointer
        if self.debug: print(f"\nFREEING {self.asset_name} ASSET POINTER AT {self.ptr}")
        Wrapper._free_asset_ptr(self.ptr)
        if self.debug: print(f"{self.asset_name} ASSET POINTER FREED\n")
        
    # -----------------------------------------------------------------------------        
    def load_from_csv(self, file_name : str):
        if not self.registered:
            raise RuntimeError("Asset must be registered before loading data")
        
        self.file_name = c_char_p(file_name.encode("utf-8"))
        Wrapper._asset_from_csv(self.ptr, self.file_name)
        self.headers = pd.read_csv(file_name, index_col=0, nrows=0).columns.tolist()
        
    # -----------------------------------------------------------------------------
    def load_from_df(self, df : pd.DataFrame, nano = False):
        if not self.registered:
            raise RuntimeError("Asset must be registered before loading data")
        
        values = df.values.flatten().astype(np.float32)
        epoch_index = df.index.values.astype(np.float32)
        if nano: epoch_index /=  1e9
        
        values_p = values.ctypes.data_as(POINTER(c_float))
        epoch_index_p = epoch_index.ctypes.data_as(POINTER(c_float))
        
        Wrapper._asset_from_pointer(
            self.ptr,
            epoch_index_p,
            values_p,
            df.shape[0],
            df.shape[1]
        )
        
        columns = df.columns
        for index, column in enumerate(columns):
            Wrapper._register_header(
                self.ptr, 
                c_char_p(column.encode("utf-8")),
                index
            )
        self.headers = columns
        
    # -----------------------------------------------------------------------------            
    def set_format(self, digit_format : str, open_col : int, close_col : int):
        """Set the format of the asset to be loaded, describes the format of the datetime as 
        well as sets the column indicies used to get market prices at every time step

        Args:
            digit_format (str): string like "%d-%d-%d" describing the format of the datetime string
            open_col (int): the column index of the open price of the asset
            close_col (int): the column index of the close price of the asset

        Raises:
            AttributeError: _description_
            AttributeError: _description_
            RuntimeError: _description_
        """

        if open_col < 0:
            raise AttributeError(f"invalid open column index passed: {open_col}")
        if close_col < 0:
            raise AttributeError(f"invalid open column index passed: {close_col}")
        if not self.registered:
            raise RuntimeError("Asset must be registered before setting asset format")
        
        Wrapper._set_asset_format(
            self.ptr,
            c_char_p(digit_format.encode("utf-8")),
            open_col,
            close_col
        )
        self.formatted = True
        
    #-----------------------------------------------------------------------------
    def set_warmup(self, warmup : int):
        """Allow for a asset to have a warmup period to load any nessecary columns that might 
        have null values in the begining. For example a 20 period moving average would need a 
        warmup of 19 if the null values are not removed before the asset is loaded.

        Args:
            warmup (int): number of rows of data to skip when executing the backtest 

        Raises:
            AttributeError: if warmup is less than 0 raise error
        """
        if warmup <= 0:
            raise AttributeError("Invalid warmup, must be positive number")
        Wrapper._set_asset_warmup(self.ptr, warmup)
        
    # -----------------------------------------------------------------------------
    def set_slippage(self, slippage : float):
        Wrapper._set_asset_slippage(self.ptr, slippage)

    # -----------------------------------------------------------------------------
    def rows(self):
        """Get the number of rows of data for the asset

        Returns:
            int: number of rows of data for the asset
        """
        return Wrapper._rows(self.ptr)
    
    # -----------------------------------------------------------------------------
    def columns(self):
        """Get the number of columns of data for the asset

        Returns:
            int: number of columns of data for the asset
        """
        return Wrapper._columns(self.ptr)

    # -----------------------------------------------------------------------------
    def index(self):
        """Get the datetime index of the asset

        Returns:
            np.array: datetime index of the asset
        """
        index_ptr = Wrapper._get_asset_index(self.ptr)
        return np.ctypeslib.as_array(index_ptr, shape=(self.rows(),))

    # -----------------------------------------------------------------------------
    def data(self):
        """Get the underlying data of the asset loaded in the C++ object

        Returns:
            np.array: 2d matrix of the asset data
        """
        data_ptr = Wrapper._get_asset_data(self.ptr)
        asset_data = np.ctypeslib.as_array(data_ptr, shape=(self.rows()*self.columns(),))
        return np.reshape(asset_data,(-1,self.columns()))
    
    # -----------------------------------------------------------------------------
    def df(self):
        """Get a dataframe representation of an Asset

        Returns:
            pd.DataFrame: a dataframe populated with a assets data, index, and headers
        """
        asset_index = self.index()
        asset_data = self.data()
        return pd.DataFrame(index = asset_index, data = asset_data, columns = self.headers)
    
    # -----------------------------------------------------------------------------
    @staticmethod
    def _index(ptr):
        index_ptr = Wrapper._get_asset_index(ptr)
        rows = Wrapper._rows(ptr)
        return np.ctypeslib.as_array(index_ptr, shape=(rows,))
        
    # -----------------------------------------------------------------------------
    @staticmethod
    def _data(ptr):
        M = Wrapper._columns(ptr)
        N = Wrapper._rows(ptr)
        data_ptr = Wrapper._get_asset_data(ptr)
        asset_data = np.ctypeslib.as_array(data_ptr, shape=(
            M*N,))
        return np.reshape(asset_data,(-1,M))

if __name__ == "__main__":
    pass