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

	virtual std::vector<Order*> next();

	Strategy(Exchange &exchange, Broker &broker);
};
class BenchmarkStrategy : public Strategy {
public:
	bool is_invested = false;
	std::vector<Order*> next();

	using Strategy::Strategy;
};


#endif