#include "pch.h"
#include "Order.h"
#include "Position.h"
#include "Asset.h"
#include "Exchange.h"
#include "Broker.h"
#include "FastTest.h"

__FastTest::__FastTest(__Exchange &exchangeObj, __Broker &brokerObj, Strategy *StrategyObj, bool logging) :
	__exchange(exchangeObj), broker(brokerObj), strategy(StrategyObj){
	this->logging = logging;
}
__FastTest::__FastTest(__Exchange &exchangeObj, __Broker &brokerObj, bool logging) :
	__exchange(exchangeObj), broker(brokerObj) {
	this->logging = logging;
}
void __FastTest::reset() {
	this->broker.reset();
	this->__exchange.reset();
	this->cash_history.clear();
	this->nlv_history.clear();
	this->filled_orders.clear();
	this->canceled_orders.clear();
}
void __FastTest::analyze_step() {
	this->cash_history.push_back(this->broker.cash);
	this->nlv_history.push_back(this->broker.net_liquidation_value);
}
void __FastTest::run() {
	if (this->logging) { printf("RUNNING FASTEST\n"); }
	this->__exchange.logging = this->logging;
	this->broker.logging = this->logging;
	this->reset();

	while (this->__exchange._get_market_view()) {
		//allow exchange to process open orders from previous steps
		if (!this->__exchange.orders.empty()) {
			filled_orders = this->__exchange.process_orders();
			this->broker.process_filled_orders(std::move(filled_orders));
		}
		//allow strategy to place orders
		this->strategy->next();

		//evaluate the portfolio
		this->broker.evaluate_portfolio();

		//evaluate strategy portfolio
		this->analyze_step();

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
}
void * CreateFastTestPtr(void *exchange_ptr, void *broker_ptr, bool logging) {
	__Exchange *__exchange_ref = static_cast<__Exchange *>(exchange_ptr);
	__Broker *__broker_ref = static_cast<__Broker *>(broker_ptr);
	__FastTest* fastTest_ptr = new __FastTest(*__exchange_ref,*__broker_ref, logging);
	fastTest_ptr->__exchange.logging = logging;
	fastTest_ptr->broker.logging = logging;
	return fastTest_ptr;
}
void DeleteFastTestPtr(void *fastTest_ptr){
	delete fastTest_ptr;
}
void reset(void *fastTest_ptr) {
	__FastTest *__fastTest_ref = static_cast<__FastTest *>(fastTest_ptr);
	__fastTest_ref->reset();
}
bool forward_pass(void *fastTest_ptr){
	__FastTest *__fastTest_ref = static_cast<__FastTest *>(fastTest_ptr);
	
	if (!__fastTest_ref->__exchange._get_market_view()) { return false; }
	//allow exchange to process open orders from previous steps
	if (!__fastTest_ref->__exchange.orders.empty()) {
		__fastTest_ref->filled_orders = __fastTest_ref->__exchange.process_orders();
		__fastTest_ref->broker.process_filled_orders(std::move(__fastTest_ref->filled_orders));
	}
	return true;
}
void backward_pass(void * fastTest_ptr) {
	
	__FastTest *__fastTest_ref = static_cast<__FastTest *>(fastTest_ptr);
	//evaluate the portfolio
	__fastTest_ref->broker.evaluate_portfolio();
	//evaluate strategy portfolio
	__fastTest_ref->analyze_step();
	//allow the exchange to clean up assets that are done streaming
	__fastTest_ref->canceled_orders = __fastTest_ref->__exchange.clean_up_market();
	if (!__fastTest_ref->canceled_orders.empty()) {
		__fastTest_ref->broker.log_canceled_orders(std::move(__fastTest_ref->canceled_orders));
	}
	//allow exchange to process cheat on close orders
	if (!__fastTest_ref->__exchange.orders.empty()) {
		__fastTest_ref->filled_orders = __fastTest_ref->__exchange.process_orders(true);
		__fastTest_ref->broker.process_filled_orders(std::move(__fastTest_ref->filled_orders));
	}
	__fastTest_ref->step_count++;
}