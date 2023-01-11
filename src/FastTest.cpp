#ifdef _WIN32
#include "pch.h"
#else
#include <sys/time.h>
#include <cstring>
#endif 
#include <unordered_set>
#include <algorithm>
#include "Order.h"
#include "Position.h"
#include "Asset.h"
#include "Exchange.h"
#include "Broker.h"
#include "FastTest.h"
#include <chrono>


__FastTest::__FastTest(__Exchange *exchange_ptr, __Broker &brokerObj, Strategy *StrategyObj, bool logging) :
	broker(brokerObj), strategy(StrategyObj){
	this->logging = logging;
	this->_register_exchange(exchange_ptr);
}
__FastTest::__FastTest(__Exchange *exchange_ptr, __Broker &brokerObj, bool logging) :
	broker(brokerObj) {
	this->logging = logging;
	this->_register_exchange(exchange_ptr);
}
void __FastTest::reset() {
	this->current_index = 0;
	this->broker.reset();
	this->filled_orders.clear();
	this->canceled_orders.clear();

	for(__Exchange* exchange : this->__exchanges){
		exchange->reset();
	}
}

std::vector<long> getUnion(std::vector<long> &v1, std::vector<long> &v2) {
    std::vector<long> unionVec;
    std::unordered_set<long> s;
    // Insert all elements of first vector 
    for (auto &i : v1) {
        s.insert(i);
    }

    // Insert all elements of second vector
    for (auto &i : v2) {
        s.insert(i);
    }
    unionVec.insert(unionVec.end(),s.begin(),s.end());
	sort(unionVec.begin(),unionVec.end());
    return unionVec;
}

void __FastTest::build(){
	this->epoch_index = this->__exchanges[0]->epoch_index;
	if(this->__exchanges.size() > 1){
		for(int i = 1; i < this->__exchanges.size(); i++){
			this->epoch_index = getUnion(this->epoch_index, this->__exchanges[i]->epoch_index);
		}
	}
}

void __FastTest::_register_benchmark(__Asset new_benchmark){
	this->benchmark = new_benchmark;
}

void __FastTest::_register_exchange(__Exchange *new_exchange){
	this->__exchanges.push_back(new_exchange);
}

void __FastTest::run() {
	if (this->logging) { printf("RUNNING FASTEST\n"); }
	for(__Exchange* exchange : this->__exchanges){
		exchange->logging = this->logging;
	}
	this->broker.logging = this->logging;
	this->reset();
	/*
	while (this->__exchange._get_market_view()) {
		//allow exchange to process open orders from previous steps
		if (!this->__exchange.orders.empty()) {
			filled_orders = this->__exchange.process_orders();
			this->broker.process_filled_orders(std::move(filled_orders));
		}
		//allow strategy to place orders
		//this->strategy->next();

		//evaluate the portfolio
		this->broker.evaluate_portfolio();

		//evaluate strategy portfolio
		this->broker.analyze_step();

		//allow the exchange to clean up assets that are done streaming
		canceled_orders = this->__exchange.clean_up_market();
		if (!canceled_orders.empty()) {
			this->broker.log_canceled_orders(std::move(canceled_orders));
		}

		//allow exchange to process cheat on close orders
		if (!this->__exchange.orders.empty()) {
			filled_orders = this->__exchange.process_orders(true);
			this->broker.process_filled_orders(std::move(filled_orders));
		}
		this->step_count++;
		if (this->logging) { printf("%i\n", step_count); }
	}
	*/
}
void * CreateFastTestPtr(void *exchange_ptr, void *broker_ptr, bool logging) {
	__Exchange *__exchange_ref = static_cast<__Exchange *>(exchange_ptr);
	__Broker *__broker_ref = static_cast<__Broker *>(broker_ptr);
	__FastTest* fastTest_ptr = new __FastTest(__exchange_ref,*__broker_ref, logging);
	fastTest_ptr->broker.logging = logging;
	return fastTest_ptr;
}
void DeleteFastTestPtr(void *ptr){
	__FastTest *__fastTest_ref = static_cast<__FastTest *>(ptr);
	delete __fastTest_ref;
}
void reset_fastTest(void *fastTest_ptr) {
	__FastTest *__fastTest_ref = static_cast<__FastTest *>(fastTest_ptr);
	__fastTest_ref->reset();
}
void build_fastTest(void *fastTest_ptr) {
	__FastTest *__fastTest_ref = static_cast<__FastTest *>(fastTest_ptr);
	__fastTest_ref->build();
}
bool forward_pass(void *fastTest_ptr){
	__FastTest *__fastTest_ref = static_cast<__FastTest *>(fastTest_ptr);

	if(__fastTest_ref->current_index == __fastTest_ref->epoch_index.size()){
		return false;
	}

	bool complete = true;
	long fasttest_time = __fastTest_ref->epoch_index[__fastTest_ref->current_index];
	for(__Exchange* exchange : __fastTest_ref->__exchanges){
		if(!exchange->epoch_index[exchange->current_index] == fasttest_time){continue;}
		if(exchange->_get_market_view()){
			complete = false;
		}
	}
	__fastTest_ref->current_index++;

	#ifdef MARGIN
	__fastTest_ref->broker.check_margin();
	#endif

	//allow exchange to process open orders from previous steps
	for(__Exchange* exchange : __fastTest_ref->__exchanges){
		if (!exchange->orders.empty()) {
			__fastTest_ref->filled_orders = exchange->process_orders();
			__fastTest_ref->broker.process_filled_orders(std::move(__fastTest_ref->filled_orders));
		}
	}
	return true;
}
void backward_pass(void * fastTest_ptr) {
	__FastTest *__fastTest_ref = static_cast<__FastTest *>(fastTest_ptr);

	//evaluate the portfolio
	__fastTest_ref->broker.evaluate_portfolio(true);

	//evaluate strategy portfolio
	__fastTest_ref->broker.analyze_step();

	//allow the exchange to clean up assets that are done streaming
	__fastTest_ref->canceled_orders.clear();
	for(__Exchange* exchange : __fastTest_ref->__exchanges){
		__fastTest_ref->canceled_orders_mid = exchange->clean_up_market();
		if(__fastTest_ref->canceled_orders_mid.size() == 0){continue;}
		__fastTest_ref->canceled_orders = combine_order_vectors(__fastTest_ref->canceled_orders, __fastTest_ref->canceled_orders_mid);
	}

	if (!__fastTest_ref->canceled_orders.empty()) {
		//Any orders for assets that have expired are canceled
		__fastTest_ref->broker.log_canceled_orders(std::move(__fastTest_ref->canceled_orders));
	}

	//allow exchange to process cheat on close orders
	for(__Exchange* exchange : __fastTest_ref->__exchanges){
		if (!exchange->orders.empty()) {
			__fastTest_ref->filled_orders = exchange->process_orders(true);
			__fastTest_ref->broker.process_filled_orders(std::move(__fastTest_ref->filled_orders));
		}
	}
	__fastTest_ref->step_count++;
}
void register_benchmark(void* fastTest_ptr, void *asset_ptr){
	__Asset * __asset_ref = static_cast<__Asset *>(asset_ptr);
	__FastTest *__fastTest_ref = static_cast<__FastTest *>(fastTest_ptr);
	__fastTest_ref->_register_benchmark(*__asset_ref);
}

void register_exchange(void * fastTest_ptr, void *exchange_ptr){
	__FastTest *__fastTest_ref = static_cast<__FastTest *>(fastTest_ptr);
	__Exchange * __exchange_ref = static_cast<__Exchange *>(exchange_ptr);
	__fastTest_ref->_register_exchange(__exchange_ref);
}

void* get_benchmark_ptr(void* fastTest_ptr){
	__FastTest *__fastTest_ref = static_cast<__FastTest *>(fastTest_ptr);
	return & __fastTest_ref->benchmark;
}