#include "pch.h"
#include <Windows.h>
#include <stdio.h>
#include <iostream>
#include <ctime>
#include <chrono>
#include <string>
#include <assert.h>

#include "utils_time.h"
#include "Asset.h"
#include "Broker.h"
#include "Exchange.h"
#include "FastTest.h"
#include "Strategy.h"
#include "Test.h"

void test_broker_limit_order(Exchange& exchange,Broker& broker)
{	
	printf("TESTING test_broker_limit_order\n");
	std::vector<order_schedule> order_scheduler = {
		order_schedule {LIMIT_ORDER,"test2",1,100,95} 
	};
	TestStrategy strategy(exchange, broker);
	FastTest ft(exchange, broker, strategy, false);
	strategy.register_test_map(order_scheduler);

	ft.run();
	assert(broker.position_history.size() == 0);

	char str_buf[28]{};
	for (int i = 0; i <= 1; i++) {
		order_scheduler[0] = order_schedule{ LIMIT_ORDER,"test2",i,100,97 };
		strategy.register_test_map(order_scheduler);
		strategy.i = 0;
		ft.run();

		assert(broker.position_history.size() == 1);
		memset(str_buf, 0, sizeof str_buf);
		timeval_to_char_array(&broker.position_history[0].position_create_time, str_buf, sizeof(str_buf));
		assert(strcmp(str_buf, test::datetime_index_multi_simple[2]) == 0);
		assert(broker.position_history[0].average_price == 97);
		assert(broker.position_history[0].close_price == 96);
	}
}
void test_broker_limit_sell(Exchange& exchange, Broker& broker){
	printf("TESTING test_broker_limit_sell\n");

	std::vector<order_schedule> order_scheduler = {
		order_schedule {LIMIT_ORDER,"test2",1,100,97},
		order_schedule {LIMIT_ORDER,"test2",3,-100,103}
	};
	TestStrategy strategy(exchange, broker);
	FastTest ft(exchange, broker, strategy, false);
	strategy.register_test_map(order_scheduler);

	ft.run();

	char str_buf[28]{};
	assert(broker.position_history.size() == 1);
	memset(str_buf, 0, sizeof str_buf);
	timeval_to_char_array(&broker.position_history[0].position_create_time, str_buf, sizeof(str_buf));
	assert(strcmp(str_buf, test::datetime_index_multi_simple[2]) == 0);
	assert(broker.position_history[0].average_price == 97);
	assert(broker.position_history[0].close_price == 103);
	assert(broker.position_history[0].realized_pl == 600);
}
void test_broker_stop_loss(Exchange& exchange, Broker& broker) {
	printf("TESTING test_broker_stop_loss\n");

	std::vector<order_schedule> order_scheduler = {
		order_schedule {MARKET_ORDER,"test2",0,100},
		order_schedule {STOP_LOSS_ORDER,"test2",1,-100,98}
	};
	TestStrategy strategy(exchange, broker);
	FastTest ft(exchange, broker, strategy, false);
	strategy.register_test_map(order_scheduler);

	ft.run();
}
bool test::test_broker() {
	std::cout << "=======TESTING BROKER====== \n";
	Exchange exchange_multi = build_simple_exchange_multi();
	Broker broker(exchange_multi, false);

	test_broker_limit_order(exchange_multi,broker);
	test_broker_limit_sell(exchange_multi, broker);
	test_broker_stop_loss(exchange_multi, broker);
	std::cout << "============================== \n";

	return true;
}