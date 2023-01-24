import sys
from ctypes import *
import os
import sys

SCRIPT_DIR = os.path.dirname(__file__)
sys.path.append(os.path.dirname(SCRIPT_DIR))

from wrapper import Wrapper
from wrapper import Broker

class Account():
    def __init__(self, account_ptr : c_void_p, account_id : int, account_name : str) -> None:
        self.account_id = account_id
        self.account_name = account_name
        self.ptr = account_ptr