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
	Exchange &exchange;
	Broker &broker;
	Strategy &strategy;

	bool logging;

	unsigned int step_count;

	std::vector<float> cash_history;
	std::vector<float> nlv_history;

	//main event lopp
	void analyze_step();
	void run();

	FastTest(Exchange &exchange, Broker &broker, Strategy &Strategy, bool logging = false);
};

#endif