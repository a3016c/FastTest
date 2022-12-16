#include "pch.h"
#include <Windows.h>
#include <assert.h>
#include "Asset.h"
#include "Exchange.h"
#include "Test.h"
#include "utils_time.h"

Exchange test::build_simple_exchange() {
	const char * test1_file_name = "test1.csv";
	Asset new_asset("test1");
	new_asset.load_from_csv(test1_file_name);

	Exchange exchange;
	exchange.register_asset(new_asset);
	exchange.build();
	return exchange;
}
Exchange test::build_simple_exchange_multi() {
	const char * test1_file_name = "test1.csv";
	const char * test2_file_name = "test2.csv";
	Asset new_asset1("test1");
	new_asset1.load_from_csv(test1_file_name);
	Asset new_asset2("test2");
	new_asset2.load_from_csv(test2_file_name);

	Exchange exchange;
	exchange.register_asset(new_asset1);
	exchange.register_asset(new_asset2);
	exchange.build();
	return exchange;
}

void test_exchange_construction() {
	std::cout << "TESTING test_exchange_construction" << std::endl;
	
	Exchange exchange = test::build_simple_exchange();
	assert(exchange.asset_counter == 1);
}
void test_exchange_get_next_time() {
	std::cout << "TESTING test_exchange_get_next_time" << std::endl;

	Exchange exchange = test::build_simple_exchange();
	assert(exchange.asset_counter == 1);
	exchange.get_market_view();

	char buf[28]{};
	timeval_to_char_array(&exchange.current_time, buf, sizeof(buf));
	assert(strcmp(buf, "2000-06-06 00:00:00.000000") == 0);

}
void test_exchange_step() {
	std::cout << "TESTING test_exchange_step" << std::endl;

	Exchange exchange = test::build_simple_exchange();
	assert(exchange.asset_counter == 1);

	std::string asset_name = "test1";
	float open[4] = { 100,102,104,105 };
	float close[4] = { 101,103,105,106 };
	const char* datetime_index[4] = { "2000-06-06 00:00:00.000000","2000-06-07 00:00:00.000000","2000-06-08 00:00:00.000000","2000-06-09 00:00:00.000000" };

	for (int i = 0; i < 4; i++) {
		exchange.get_market_view();
		char buf[28]{};
		timeval_to_char_array(&exchange.current_time, buf, sizeof(buf));
		assert(strcmp(buf, datetime_index[i]) == 0);
		assert(exchange.get_market_price(asset_name, true) == close[i]);
		assert(exchange.get_market_price(asset_name, false) == open[i]);
	}
}
void test_exchange_setup_multi() {
	std::cout << "TESTING test_exchange_setup_multi" << std::endl;

	Exchange exchange = test::build_simple_exchange_multi();
	assert(exchange.asset_counter == 2);

	const char* datetime_index[6] = { "2000-06-05 00:00:00.000000","2000-06-06 00:00:00.000000",
		"2000-06-07 00:00:00.000000","2000-06-08 00:00:00.000000",
		"2000-06-09 00:00:00.000000","2000-06-12 00:00:00.000000" };
	float open1[4] = { 100,102,104,105 };
	float close1[4] = { 101,103,105,106 };
	float open2[6] = { 101,100,98,101,101,103};
	float close2[6] = { 101.5,99,97,101.5,101.5,96};

	for (int i = 0; i < 6; i++) {
		exchange.get_market_view();
		char buf[28]{};
		timeval_to_char_array(&exchange.current_time, buf, sizeof(buf));
		assert(strcmp(buf, datetime_index[i]) == 0);
		assert(exchange.market_view["test2"]->get(0) == open2[i]);
		assert(exchange.market_view["test2"]->get(1) == close2[i]);
		
		if ((i >= 1) & (i < 5)) {
			assert(exchange.market_view["test1"]->get(0) == open1[i-1]);
			assert(exchange.market_view["test1"]->get(1) == close1[i - 1]);
		}
		else {
			assert(exchange.market_view.count("test1") == 0);
		}
		exchange.clean_up_market();
	}
}
bool test::test_exchange() {
	std::cout << "=======TESTING EXCHANGE====== \n";
	test_exchange_construction();
	test_exchange_get_next_time();
	test_exchange_step();
	test_exchange_setup_multi();
	std::cout << "============================== \n";

	return true;
}