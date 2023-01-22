import sys
from ctypes import *
import os
import sys

SCRIPT_DIR = os.path.dirname(__file__)
sys.path.append(os.path.dirname(SCRIPT_DIR))
from wrapper import Wrapper


class Account():
    def __init__(self, account_id : int) -> None:
        self.account_id = account_id
        self.ptr = Wrapper._new_account_ptr(self.account_id)
        
    def __del__(self):
        Wrapper._free_account_ptr(self.ptr)
    
    def reset(self):
        Wrapper._reset_account(self.ptr)