#include "pch.h"
#include <Windows.h>
#include <assert.h>

#include "Strategy.h"
#include "Asset.h"
#include "Broker.h"
#include "Exchange.h"
#include "FastTest.h"
#include "Test.h"
#include "utils_time.h"

void test_ft_construction() {
	std::cout << "TESTING test_ft_construction" << std::endl;
	Exchange exchange = test::build_simple_exchange();
	Broker broker(exchange);
	Strategy strategy(exchange, broker);
	FastTest ft(exchange, broker, strategy);

	ft.run();
	assert(ft.exchange.asset_counter == 0);
	assert(ft.exchange.current_time.tv_sec == 960526800);
	assert(ft.exchange.market.size() == 0);
}
void test_ft_reset() {
	std::cout << "TESTING test_ft_reset" << std::endl;
	Exchange exchange = test::build_simple_exchange();
	Broker broker(exchange);
	Strategy strategy(exchange, broker);
	FastTest ft(exchange, broker, strategy);

	ft.run();
	assert(ft.exchange.asset_counter == 0);
	assert(ft.exchange.current_time.tv_sec == 960526800);
	assert(ft.exchange.market.size() == 0);

	ft.reset();
	assert(ft.exchange.market.size() == 1);
	ft.run();
	assert(ft.exchange.asset_counter == 0);
	assert(ft.exchange.current_time.tv_sec == 960526800);
	assert(ft.exchange.market.size() == 0);
}
bool test::test_ft() {
	std::cout << "=======TESTING FASTEST====== \n";
	test_ft_construction();
	test_ft_reset();
	std::cout << "============================== \n";

	return true;
}