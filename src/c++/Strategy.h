#pragma once
#ifndef STRATEGY_H // include guard
#define STRATEGY_H
#include "Exchange.h"
#include "Broker.h"
#include <vector>
#include "Order.h"

class Strategy
{
public:
	__Exchange &__exchange;
	__Broker &__broker;

	virtual void next();

	Strategy(__Exchange &__exchange, __Broker &broker);
	Strategy() = default;
};
struct order_schedule {
	OrderType order_type = MARKET_ORDER;
	UINT asset_id;
	int i;
	float units;
	float limit = 0;
};
class TestStrategy : public Strategy {
public:
	int i = 0;
	std::vector<order_schedule> order_scheduler;
	void register_test_map(std::vector<order_schedule> orders);
	void next();
	TestStrategy() = default;
	using Strategy::Strategy;
};


#endif