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

void test::TestStrategy::register_test_map(std::map<int, order_schedule> orders) {
	this->orders = orders;
}

std::vector<Order> test::TestStrategy::next() {
	std::vector<Order> new_orders;
	for (const auto& kvp : this->orders) {
		if (kvp.first == i) {
			MarketOrder new_order(
				kvp.second.asset_name,
				kvp.second.units
			);
			new_orders.push_back(new_order);
		}
	}
	i++;
	return new_orders;
}