#include "pch.h"
#include <Windows.h>
#include <assert.h>

#include "Strategy.h"
#include "Asset.h"
#include "Broker.h"
#include "Exchange.h"
#include "FastTest.h"
#include "Test.h"
#include "Strategy.h"
#include "utils_time.h"


#include <chrono>
using namespace std::chrono;

const char* datetime_index[4] = { "2000-06-06 00:00:00.000000","2000-06-07 00:00:00.000000","2000-06-08 00:00:00.000000","2000-06-09 00:00:00.000000" };

void test_strategy_construction() {
	std::cout << "TESTING test_strategy_construction" << std::endl;
	Exchange exchange = test::build_simple_exchange();
	Broker broker(exchange);
	Strategy strategy(exchange, broker);
	FastTest ft(exchange, broker, strategy);

	assert(strategy.exchange.asset_counter == 1);
	assert(ft.exchange.asset_counter == 1);
	assert(&ft.exchange == &strategy.exchange);
}
void test_benchmark_strategy() {
	std::cout << "TESTING test_benchmark_strategy" << std::endl;
	Exchange exchange = test::build_simple_exchange();
	Broker broker(exchange, false);
	BenchmarkStrategy strategy(exchange, broker);
	FastTest ft(exchange, broker, strategy, false);

	ft.run();

	assert(ft.exchange.current_time.tv_sec == 960526800);
	assert(broker.net_liquidation_value - 104950.492 < .001);
	assert(broker.cash - 104950.492 < .001);
	assert(broker.position_history.size() == 1);
	assert((int)broker.position_history[0].average_price == 101);
	assert((int)broker.position_history[0].close_price == 106);

	char buf_open[28]{};
	char buf_close[28]{};
	timeval_to_char_array(&broker.position_history[0].position_create_time, buf_open, sizeof(buf_open));
	timeval_to_char_array(&broker.position_history[0].position_close_time, buf_close, sizeof(buf_close));
	assert(strcmp(buf_open, datetime_index[0]) == 0);
	assert(strcmp(buf_close, datetime_index[3]) == 0);
}
void test_increase_strategy() {
	std::cout << "TESTING test_increase_strategy" << std::endl;
	Exchange exchange = test::build_simple_exchange();
	Broker broker(exchange, false);

	std::map<int, test::order_schedule> orders = { 
		{0 , test::order_schedule {100,"test1"}},
		{1 , test::order_schedule {100,"test1"}},
	};
	test::TestStrategy strategy(exchange, broker);
	strategy.register_test_map(orders);
	FastTest ft(exchange, broker, strategy, false);

	ft.run();

	assert(broker.order_history.size() == 2);
	assert((int)broker.order_history[0].fill_price == 102);
	assert((int)broker.order_history[1].fill_price == 104);
	assert(broker.position_history.size() == 1);
	assert((int)broker.position_history[0].average_price == 103);
	assert((int)broker.position_history[0].close_price == 106);
	assert((int)broker.position_history[0].realized_pl == 600);
	std::vector<float> cash = { 100000,89800,79400,100600};
	std::vector<float> nlv = { 100000,100100,100400,100600 };
	assert(cash == ft.cash_history);
	assert(nlv == ft.nlv_history);
}
void test_reduce_strategy() {
	std::cout << "TESTING test_reduce_strategy" << std::endl;
	Exchange exchange = test::build_simple_exchange();
	Broker broker(exchange, true);
	
	std::map<int, test::order_schedule> orders = {
	{0 , test::order_schedule {100,"test1"}},
	{1 , test::order_schedule {-50,"test1"}},
	};
	test::TestStrategy strategy(exchange, broker);
	strategy.register_test_map(orders);

	FastTest ft(exchange, broker, strategy, true);
	ft.run();

	assert(broker.order_history.size() == 2);
	assert((int)broker.order_history[0].units == 100);
	assert((int)broker.order_history[1].units == -50);
	assert(broker.position_history.size() == 1);
	assert((int)broker.position_history[0].average_price == 102);
	assert((int)broker.position_history[0].realized_pl == 300);
	std::vector<float> cash = { 100000,89800,95000,100300 };
	std::vector<float> nlv = { 100000,100100,100250,100300 };
	assert(cash == ft.cash_history);
	assert(nlv == ft.nlv_history);
}
bool test::test_strategy() {
	std::cout << "=======TESTING STRATEGY====== \n";
	test_strategy_construction();
	test_benchmark_strategy();
	test_increase_strategy();
	test_reduce_strategy();
	std::cout << "============================== \n";

	return true;
}