#pragma once
#ifndef FAST_TEST_H // include guard
#define FAST_TEST_H
#ifdef ASSET_EXPORTS
#define FAST_API __declspec(dllexport)
#else
#define FAST_API __declspec(dllimport)
#endif
#include <vector>
#include <string>
#include "Exchange.h"
#include "Strategy.h"
#include "Broker.h"
#include "Order.h"

class __FastTest {
public:
	__Exchange &__exchange;
	__Broker &broker;
	Strategy *strategy;

	bool logging;

	unsigned int step_count = 0;

	std::vector<float> cash_history;
	std::vector<float> nlv_history;
	std::vector<std::unique_ptr<Order>> filled_orders;
	std::vector<std::unique_ptr<Order>> canceled_orders;

	void reset();

	//main event lopp
	void analyze_step();
	inline void run();

	__FastTest(__Exchange &exchange, __Broker &broker, Strategy *Strategy, bool logging = false);
	__FastTest(__Exchange &exchange, __Broker &broker, bool logging = false);
};
extern "C" {
	FAST_API void * CreateFastTestPtr(void *exchange_ptr, void *broker_ptr, bool logging = true);
	FAST_API void DeleteFastTestPtr(void *ptr);
	FAST_API void reset_fastTest(void *exchange_ptr);

	FAST_API bool forward_pass(void* fastTest_ptr);
	FAST_API void backward_pass(void* fastTest_ptr);

	FAST_API float* get_nlv_history(void* fastTest_ptr);
	FAST_API float* get_has_history(void* fastTest_ptr);
}

#endif