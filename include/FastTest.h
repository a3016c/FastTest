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
#include "Position.h"
#include "Strategy.h"
#include "Asset.h"
#include "Broker.h"
#include "Order.h"

class __FastTest {
public:

	bool logging = false;
	bool debug = false;

	bool save_last_portfolio = false;
	std::unordered_map<unsigned int, Position> portfolio; 

	unsigned int      current_index = 0;
	std::vector<long> epoch_index;
	unsigned int      step_count = 0;

	std::vector<__Exchange*> __exchanges;
	__Broker                     *broker;
	Strategy                   *strategy;

	__Asset benchmark; 

	std::vector<std::unique_ptr<Order>> filled_orders;
	std::vector<std::unique_ptr<Order>> canceled_orders;

	//function to register a benchmark to compare results too
	void _register_benchmark(__Asset new_benchmark);

	//function to register a new exchange to the fast test;
	void _register_exchange(__Exchange* new_exchange);

	//function to register a new broker to the fast test;
	void _register_broker(__Broker* new_broker);

	//function to build fasttest on setup
	void build();

	//function to reset fasttest and member objects
	void reset();

	//function to save positions to a PositionArray to pass through C api
	void copy_positions_on_end();

	//main event lopp
	void analyze_step();
	inline void run();

	__FastTest(Strategy *Strategy, bool logging = false, bool debug = false, bool save_last_portfolio = false);
	__FastTest(bool logging = false, bool debug = false, bool save_last_portfolio = false);
};

extern "C" {
	FAST_API void * CreateFastTestPtr(bool logging = true, bool debug = false, bool save_last_portfolio = false);
	FAST_API void DeleteFastTestPtr(void *ptr);
	FAST_API void reset_fastTest(void *exchange_ptr);

	FAST_API void build_fastTest(void *fastTest_ptr);

	FAST_API bool forward_pass(void* fastTest_ptr);
	FAST_API void backward_pass(void* fastTest_ptr);

	FAST_API void register_benchmark(void* fastTest_ptr, void *asset_ptr);
	FAST_API void register_exchange(void* fastTest_ptr, void *exchange_ptr, unsigned int exchange_id);
	FAST_API void register_broker(void* fastTest_ptr, void *broker_ptr, unsigned int broker_id);
	
	FAST_API void * get_benchmark_ptr(void* fastTest_ptr);
	FAST_API size_t get_fasttest_index_length(void* fastTest_ptr);
	FAST_API long * get_fasttest_datetime_index(void* fastTest_ptr);

	FAST_API size_t get_portfolio_size(void* fastTest_ptr);
	FAST_API void get_last_positions(void *fastTest_ptr, PositionArray *position_array);

}

#endif