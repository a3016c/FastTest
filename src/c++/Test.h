#pragma once
#ifndef TEST_H // include guard
#define TEST_H
#include "Strategy.h"
#include "Exchange.h"
#include <vector>
#include <map>

namespace test
{
	Exchange build_simple_exchange();
	Exchange build_simple_exchange_multi();
	bool test_asset();
	bool test_exchange();
	bool test_ft();
	bool test_strategy();

	struct order_schedule {
		int i;
		float units;
		std::string asset_name;
	};

	class TestStrategy : public Strategy {
	public:
		int i = 0;
		std::vector<order_schedule> orders;
		void register_test_map(std::vector<order_schedule> orders);
		std::vector<Order> next();
		using Strategy::Strategy;
	};
}

#endif