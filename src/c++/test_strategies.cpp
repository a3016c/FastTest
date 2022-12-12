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

void test::TestStrategy::register_test_map(std::vector<order_schedule>orders) {
	this->orders = orders;
}

std::vector<Order> test::TestStrategy::next() {
	std::vector<Order> new_orders;
	for (auto it = this->orders.begin(); it != this->orders.end();) {
		if (it->i == i) {
			MarketOrder new_order(
				it->asset_name,
				it->units
			);
			new_orders.push_back(new_order);
			it = this->orders.erase(it);
		}
		else {
			it++;
		}
	}
	i++;
	return new_orders;
}