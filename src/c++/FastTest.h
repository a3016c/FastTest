#pragma once
#ifndef FAST_TEST_H // include guard
#define FAST_TEST_H
#include <vector>
#include <string>
#include "Exchange.h"
#include "Strategy.h"
#include "Broker.h"
#include "Order.h"

class FastTest {
public:
	__Exchange &__exchange;
	Broker &broker;
	Strategy &strategy;

	bool logging;

	unsigned int step_count = 0;

	std::vector<float> cash_history;
	std::vector<float> nlv_history;

	void reset();

	//main event lopp
	void analyze_step();
	void run();
	void build();

	FastTest(__Exchange &exchange, Broker &broker, Strategy &Strategy, bool logging = false);
};

#endif