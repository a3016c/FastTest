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

void test_strategy_construction() {
	printf("TESTING test_strategy_construction\n");
	Exchange exchange = test::build_simple_exchange();
	Broker broker(exchange);
	Strategy strategy(exchange, broker);
	FastTest ft(exchange, broker, strategy);

	assert(strategy.exchange.asset_counter == 1);
	assert(ft.exchange.asset_counter == 1);
	assert(&ft.exchange == &strategy.exchange);
}
void test_benchmark_strategy() {
	printf("TESTING test_benchmark_strategy\n");
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
	assert(strcmp(buf_open, test::datetime_index_simple[0]) == 0);
	assert(strcmp(buf_close, test::datetime_index_simple[3]) == 0);
}
void test_increase_strategy() {
	printf("TESTING test_increase_strategy\n");
	Exchange exchange = test::build_simple_exchange();
	Broker broker(exchange, false);

	std::vector<order_schedule> orders = { 
		order_schedule {MARKET_ORDER,"test1",0,100,},
		order_schedule {MARKET_ORDER,"test1",1,100,}};
	TestStrategy strategy(exchange, broker);
	strategy.register_test_map(orders);
	FastTest ft(exchange, broker, strategy, false);

	ft.run();

	assert(broker.order_history.size() == 2);
	assert((int)broker.order_history[0]->fill_price == 102);
	assert((int)broker.order_history[1]->fill_price == 104);
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
	Broker broker(exchange, false);
	
	std::vector<order_schedule> orders = {
		order_schedule {MARKET_ORDER,"test1",0,100},
		order_schedule {MARKET_ORDER,"test1",1,-50}};
	TestStrategy strategy(exchange, broker);
	strategy.register_test_map(orders);

	FastTest ft(exchange, broker, strategy, false);
	ft.run();

	assert(broker.order_history.size() == 2);
	assert((int)broker.order_history[0]->units == 100);
	assert((int)broker.order_history[1]->units == -50);
	assert(broker.position_history.size() == 1);
	assert((int)broker.position_history[0].average_price == 102);
	assert((int)broker.position_history[0].realized_pl == 300);
	std::vector<float> cash = { 100000,89800,95000,100300 };
	std::vector<float> nlv = { 100000,100100,100250,100300 };
	assert(cash == ft.cash_history);
	assert(nlv == ft.nlv_history);
}
void test_multi_asset_strategy() {
	std::cout << "TESTING test_multi_asset_strategy" << std::endl;
	Exchange exchange = test::build_simple_exchange_multi();
	Broker broker(exchange, false);

	std::vector<order_schedule> orders = {
	order_schedule {MARKET_ORDER,"test2",0,100},
	order_schedule {MARKET_ORDER,"test1",2,100},
	order_schedule {MARKET_ORDER,"test2",4,-100},};
	TestStrategy strategy(exchange, broker);
	strategy.register_test_map(orders);
	FastTest ft(exchange, broker, strategy, false);
	ft.run();

	assert(broker.order_history.size() == 3);
	assert(broker.position_history.size() == 2);
	assert((int)broker.position_history[0].average_price == 104);
	assert((int)broker.position_history[0].close_price == 106);
	assert((int)broker.position_history[1].average_price == 100);
	assert((int)broker.position_history[1].close_price == 103);
	std::vector<float> cash = { 100000,90000,90000,79600,90200,100500};
	std::vector<float> nlv = { 100000,99900,99700,100250,100350,100500};

	assert(cash == ft.cash_history);
	assert(nlv == ft.nlv_history);
}
void test_limit_order() {
	std::cout << "TESTING test_limit_order" << std::endl;
	const char * test1_file_name = "test3_A_US.csv";
	AssetDataFormat format("%d-%d-%d",0,3);
	Asset new_asset("A",format);
	new_asset.load_from_csv(test1_file_name);

	Exchange exchange;
	exchange.register_asset(new_asset);
	exchange.build();
	Broker broker(exchange, false);

	std::vector<order_schedule> orders = {
	order_schedule {LIMIT_ORDER,"A",20,100,39.99}
	};
	TestStrategy strategy(exchange, broker);
	strategy.register_test_map(orders);
	FastTest ft(exchange, broker, strategy, false);
	ft.run();

	char buf_open[28]{};
	char buf_close[28]{};
	const char* datetime_index_real[2] = { "2000-05-23 00:00:00.000000","2001-01-31 00:00:00.000000"};
	timeval_to_char_array(&broker.position_history[0].position_create_time, buf_open, sizeof(buf_open));
	timeval_to_char_array(&broker.position_history[0].position_close_time, buf_close, sizeof(buf_close));
	assert(strcmp(buf_open, datetime_index_real[0]) == 0);
	assert(strcmp(buf_close, datetime_index_real[1]) == 0);
	assert(broker.position_history[0].average_price - 37.7471 < .001);
}

bool test::test_strategy() {
	std::cout << "=======TESTING STRATEGY====== \n";
	test_strategy_construction();
	test_benchmark_strategy();
	test_increase_strategy();
	test_reduce_strategy();
	test_multi_asset_strategy();
	test_limit_order();
	std::cout << "============================== \n";

	return true;
}