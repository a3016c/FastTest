#pragma once
#ifndef FAST_TEST_H // include guard
#define FAST_TEST_H
#ifdef _WIN32
#define FAST_API __declspec(dllexport)
#else
#define FAST_API
#endif
#include <vector>
#include <string>
#include "Exchange.h"
#include "Strategy.h"
#include "Asset.h"
#include "Broker.h"
#include "Order.h"

class __FastTest {
public:

	std::vector<__Exchange*> __exchanges;
	unsigned int current_index = 0;
	std::vector<long> epoch_index;

	__Broker &broker;
	Strategy *strategy;

	__Asset benchmark; 

	bool logging;
	bool debug;
	unsigned int step_count = 0;

	std::vector<std::unique_ptr<Order>> filled_orders;
	std::vector<std::unique_ptr<Order>> canceled_orders;
	std::vector<std::unique_ptr<Order>> canceled_orders_mid;

	//function to register a benchmark to compare results too
	void _register_benchmark(__Asset new_benchmark);

	//function to register a new exchange to the fast test;
	void _register_exchange(__Exchange* new_exchange);

	//function to build fasttest on setup
	void build();

	//function to reset fasttest and member objects
	void reset();

	//main event lopp
	void analyze_step();
	inline void run();

	__FastTest(__Broker &broker, Strategy *Strategy, bool logging = false, bool debug = false);
	__FastTest(__Broker &broker, bool logging = false, bool debug = false);
};

extern "C" {
	FAST_API void * CreateFastTestPtr(void *broker_ptr, bool logging = true, bool debug = false);
	FAST_API void DeleteFastTestPtr(void *ptr);
	FAST_API void reset_fastTest(void *exchange_ptr);

	FAST_API void build_fastTest(void *fastTest_ptr);

	FAST_API bool forward_pass(void* fastTest_ptr);
	FAST_API void backward_pass(void* fastTest_ptr);

	FAST_API void register_benchmark(void* fastTest_ptr, void *asset_ptr);
	FAST_API void register_exchange(void* fastTest_ptr, void *asset_ptr, unsigned int exchange_id);
	FAST_API void * get_benchmark_ptr(void* fastTest_ptr);

}

#endif