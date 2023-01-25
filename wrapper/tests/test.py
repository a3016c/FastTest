import unittest
from io import StringIO
from test_asset import AssetTestMethods
from test_broker import BrokerTestMethods
from test_exchange import ExchangeTestMethods
from test_strategy import StrategyTestMethods
from test_account import AccountTestMethods
from test_ft import FTTestMethods


from pprint import pprint
stream = StringIO()
runner = unittest.TextTestRunner(stream=stream)

result = runner.run(unittest.makeSuite(AssetTestMethods))
print('Tests run ', result.testsRun)
print('Errors ', result.errors)
pprint(result.failures)
stream.seek(0)
print('Test output\n', stream.read())

result = runner.run(unittest.makeSuite(BrokerTestMethods))
print('Tests run ', result.testsRun)
print('Errors ', result.errors)
pprint(result.failures)
stream.seek(0)
print('Test output\n', stream.read())

result = runner.run(unittest.makeSuite(ExchangeTestMethods))
print('Tests run ', result.testsRun)
print('Errors ', result.errors)
pprint(result.failures)
stream.seek(0)
print('Test output\n', stream.read())

result = runner.run(unittest.makeSuite(FTTestMethods))
print('Tests run ', result.testsRun)
print('Errors ', result.errors)
pprint(result.failures)
stream.seek(0)
print('Test output\n', stream.read())

result = runner.run(unittest.makeSuite(StrategyTestMethods))
print('Tests run ', result.testsRun)
print('Errors ', result.errors)
pprint(result.failures)
stream.seek(0)
print('Test output\n', stream.read())

result = runner.run(unittest.makeSuite(AccountTestMethods))
print('Tests run ', result.testsRun)
print('Errors ', result.errors)
pprint(result.failures)
stream.seek(0)
print('Test output\n', stream.read())

