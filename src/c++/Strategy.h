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
	Exchange &exchange;
	Broker &broker;

	virtual std::vector<std::unique_ptr<Order>> next();

	Strategy(Exchange &exchange, Broker &broker);
};
class BenchmarkStrategy : public Strategy {
public:
	bool is_invested = false;
	std::vector<std::unique_ptr<Order>> next();

	using Strategy::Strategy;
};
struct order_schedule {
	OrderType order_type = MARKET_ORDER;
	std::string asset_name;
	int i;
	float units;
	float limit = 0;
};
class TestStrategy : public Strategy {
public:
	int i = 0;
	std::vector<order_schedule> orders;
	void register_test_map(std::vector<order_schedule> orders);
	std::vector<std::unique_ptr<Order>> next();
	using Strategy::Strategy;
};


#endif