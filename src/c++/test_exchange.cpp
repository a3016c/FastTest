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
	exchange.get_next_time();

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
		exchange.step();
		char buf[28]{};
		timeval_to_char_array(&exchange.current_time, buf, sizeof(buf));
		assert(strcmp(buf, datetime_index[i]) == 0);
		assert(exchange.get_market_price(asset_name, true) == close[i]);
		assert(exchange.get_market_price(asset_name, false) == open[i]);
	}

}
bool test::test_exchange() {
	std::cout << "=======TESTING EXCHANGE====== \n";
	test_exchange_construction();
	test_exchange_get_next_time();
	test_exchange_step();
	std::cout << "============================== \n";

	return true;
}