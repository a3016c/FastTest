# FastTest

High performance C++ backtesting library with a python wrapper for Algorithmic trading 

## Installation

```bash
git clone https://github.com/ntorm1/FastTest.git
cd FastTest
cmake -B build
cd build
make
```

Google Colab
To avoid any build problems you can use Google Colab which has been tested. To install:
```bash
!git clone https://github.com/ntorm1/FastTest.git
!cd /content/FastTest && git pull
!cd /content/FastTest && cmake -B build
!cd /content/FastTest/build && make -j
!cd /content/FastTest/wrapper/tests && python test.py
```

Then you can access the Library as follows:
```python
sys.path.append("/content/FastTest/wrapper")
from Exchange import Exchange, Asset
from Broker import Broker
from Strategy import Strategy
from FastTest import FastTest
```

## Tests
```bash
cd ../Wrapper/tests
python3 test.py
```

