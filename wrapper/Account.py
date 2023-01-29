import sys
from ctypes import *
import os
import numpy as np

SCRIPT_DIR = os.path.dirname(__file__)
sys.path.append(os.path.dirname(SCRIPT_DIR))
from wrapper import Wrapper

class Account():
    # -----------------------------------------------------------------------------  
    def __init__(self, account_id : int, account_name : str, cash : float, debug = False) -> None:
        self.account_id = account_id
        self.account_name = account_name
        self.alloc = False
        self.debug = debug
        
        self.ptr = Wrapper._new_account_ptr(account_id, cash)
    
    # -----------------------------------------------------------------------------          
    def __del__(self):
        if self.debug: print(f"\nFREEING {self.account_name} ACCOUNT POINTER AT {self.ptr}")
        Wrapper._free_account_ptr(self.ptr)
        if self.debug: print(f"{self.account_name} ACCOUNT POINTER FREED\n")

    # -----------------------------------------------------------------------------  
    def get_history_length(self):
        """_summary_

        Returns:
            int: the length of the nlv_history of the broker (how many valuations of the portfolio there were)
        """
        return Wrapper._account_get_history_length(self.ptr)
    
    # -----------------------------------------------------------------------------  
    def get_cash_history(self):
        """_summary_

        Returns:
            numpy array: an array of doubles representing available cash at every time period 
        """
        cash_ptr = Wrapper._account_get_cash_history(self.ptr)
        return np.ctypeslib.as_array(cash_ptr, shape=(self.get_history_length(),))
    
    # -----------------------------------------------------------------------------  
    def get_nlv_history(self):
        """_summary_

        Returns:
            numpy array: an array of doubles representing net liquidation value at every time period 
        """
        nlv_ptr = Wrapper._account_get_nlv_history(self.ptr)
        return np.ctypeslib.as_array(nlv_ptr, shape=(self.get_history_length(),))
    