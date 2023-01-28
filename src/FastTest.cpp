#ifdef _WIN32
#include "pch.h"
#else
#include <sys/time.h>
#include <cstring>
#endif 
#include <unordered_set>
#include <algorithm>
#include <chrono>
#include "utils_vector.h"
#include "Order.h"
#include "Position.h"
#include "Asset.h"
#include "Exchange.h"
#include "Broker.h"
#include "FastTest.h"

__FastTest::__FastTest(Strategy *StrategyObj, bool logging, bool debug, bool save_last_portfolio):
	strategy(StrategyObj){
	this->logging = logging;
	this->debug = debug;
}
__FastTest::__FastTest(bool logging, bool debug, bool save_last_portfolio) {
	this->logging = logging;
	this->debug = debug;
	this->save_last_portfolio = save_last_portfolio;
}
void __FastTest::reset() {
	this->current_index = 0;
	this->broker->reset();
	this->filled_orders.clear();
	this->canceled_orders.clear();

	for(__Exchange* exchange : this->__exchanges){
		exchange->reset();
	}
}

void __FastTest::build(){
	if(this->debug){
		printf("BUILDING FASTTEST \n");
	}

	for(auto const & exchange : this->__exchanges){
		exchange->build();
	}

	if(this->debug){
		printf("EXCHANGES BUILT \n");
	}

	this->epoch_index = this->__exchanges[0]->epoch_index;
	if(this->__exchanges.size() > 1){
		for(int i = 1; i < this->__exchanges.size(); i++){
			this->epoch_index = getUnion(this->epoch_index, this->__exchanges[i]->epoch_index);
		}
	}
	
	if(this->debug){
		printf("FASTTEST BUILT \n");
	}
}

void __FastTest::_register_benchmark(__Asset new_benchmark){
	this->benchmark = new_benchmark;
}

void __FastTest::_register_broker(__Broker *new_broker){
	this->broker = new_broker;
}

void __FastTest::_register_exchange(__Exchange *new_exchange){
	new_exchange->is_registered = true;
	this->__exchanges.push_back(new_exchange);
}

void __FastTest::copy_positions_on_end(){
	this->portfolio.clear();
	for (auto & pair : this->broker->accounts){
		auto & account = pair.second;
		for (auto it = account->portfolio.begin(); it != account->portfolio.end();) {
			Position position =  it->second;	
			unsigned int exchange_id = position.exchange_id;
        	__Exchange *exchange = this->broker->exchanges[exchange_id];
        	float market_price = exchange->_get_market_price(position.asset_id, true);	

			position.evaluate(market_price, true);
			this->portfolio[position.asset_id] = position;
			it++;
		}
	}
}

void __FastTest::run() {
	if (this->logging) { printf("RUNNING FASTEST\n"); }
	for(__Exchange* exchange : this->__exchanges){
		exchange->logging = this->logging;
	}
	this->broker->logging = this->logging;
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
void * CreateFastTestPtr(bool logging, bool debug, bool save_last_portfolio) {
	__FastTest* fastTest_ptr = new __FastTest(logging, debug, save_last_portfolio);
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

	if(__fastTest_ref->debug){
		printf("ENTERING FORWARD PASS\n");
	}

	//reached end of the test
	if(__fastTest_ref->current_index == __fastTest_ref->epoch_index.size()){
		return false;
	}

	long fasttest_time = __fastTest_ref->epoch_index[__fastTest_ref->current_index];
	
	if(__fastTest_ref->debug){
		printf("TIME: %ld\n", fasttest_time);
	}

	//set the market view for all exchanges that are at the current time
	for(__Exchange* exchange : __fastTest_ref->__exchanges){
		if(!(exchange->epoch_index[exchange->current_index] == fasttest_time)){continue;}
		if(exchange->_get_market_view()){
		}
	}
	__fastTest_ref->current_index++;

	#ifdef MARGIN
	__fastTest_ref->broker->check_margin();
	#endif

	//evaluate the portfolio
	__fastTest_ref->broker->evaluate_portfolio(false);

	//allow exchange to process open orders from previous steps
	for(__Exchange* exchange : __fastTest_ref->__exchanges){
		if (!exchange->orders.empty()) {
			__fastTest_ref->filled_orders = exchange->process_orders();
			__fastTest_ref->broker->process_filled_orders(std::move(__fastTest_ref->filled_orders));
		}
	}

	if(__fastTest_ref->debug){
		printf("EXITING FORWARD PASS\n");
	}

	return true;
}
void backward_pass(void * fastTest_ptr) {
	__FastTest *__fastTest_ref = static_cast<__FastTest *>(fastTest_ptr);

	if(__fastTest_ref->debug){
		printf("ENTERING BACKWARD PASS\n");
	}

	//if we are at the last step and save_last_portfolio is true, then add a copy of all open positions into the 
	//fasttest portfolio member to be able to access once the test is complete
	if(__fastTest_ref->save_last_portfolio){
		if(__fastTest_ref->current_index == __fastTest_ref->epoch_index.size()){
		__fastTest_ref->copy_positions_on_end();
		}
	}

	//evaluate the portfolio
	__fastTest_ref->broker->evaluate_portfolio(true);

	//evaluate strategy portfolio
	__fastTest_ref->broker->analyze_step();

	//allow the exchange to clean up assets that are done streaming
	__fastTest_ref->canceled_orders.clear();
	std::vector<std::unique_ptr<Order>> canceled_orders;
	for(__Exchange* exchange : __fastTest_ref->__exchanges){
		exchange->clean_up_market(canceled_orders);
	}

	if (!__fastTest_ref->canceled_orders.empty()) {
		//Any orders for assets that have expired are canceled
		__fastTest_ref->broker->log_canceled_orders(std::move(__fastTest_ref->canceled_orders));
	}

	//allow exchange to process cheat on close orders
	for(__Exchange* exchange : __fastTest_ref->__exchanges){
		if (!exchange->orders.empty()) {
			__fastTest_ref->filled_orders = exchange->process_orders(true);
			__fastTest_ref->broker->process_filled_orders(std::move(__fastTest_ref->filled_orders));
		}
	}

	__fastTest_ref->step_count++;

	if(__fastTest_ref->debug){
		printf("EXITING BACKWARD PASS\n\n\n");
	}
}
void register_benchmark(void* fastTest_ptr, void *asset_ptr){
	__Asset * __asset_ref = static_cast<__Asset *>(asset_ptr);
	__FastTest *__fastTest_ref = static_cast<__FastTest *>(fastTest_ptr);
	__fastTest_ref->_register_benchmark(*__asset_ref);
}
void register_exchange(void * fastTest_ptr, void *exchange_ptr, unsigned int exchange_id){
	__FastTest *__fastTest_ref = static_cast<__FastTest *>(fastTest_ptr);
	__Exchange * __exchange_ref = static_cast<__Exchange *>(exchange_ptr);
	__exchange_ref->exchange_id = exchange_id;
	__fastTest_ref->_register_exchange(__exchange_ref);
}
void register_broker(void * fastTest_ptr, void *broker_ptr, unsigned int broker_id){
	__FastTest *__fastTest_ref = static_cast<__FastTest *>(fastTest_ptr);
	__Broker * __broker_ref = static_cast<__Broker *>(broker_ptr);
	__broker_ref->broker_id = broker_id;
	__fastTest_ref->_register_broker(__broker_ref);
}
void* get_benchmark_ptr(void* fastTest_ptr){
	__FastTest *__fastTest_ref = static_cast<__FastTest *>(fastTest_ptr);
	return & __fastTest_ref->benchmark;
}
size_t get_fasttest_index_length(void * fastTest_ptr){
	__FastTest * __fastTest_ref = static_cast<__FastTest *>(fastTest_ptr);
	return __fastTest_ref->epoch_index.size();
}
long * get_fasttest_datetime_index(void *fastTest_ptr){
	__FastTest * __fastTest_ref = static_cast<__FastTest *>(fastTest_ptr);
	return __fastTest_ref->epoch_index.data();
}
size_t get_portfolio_size(void *fastTest_ptr){
	__FastTest * __fastTest_ref = static_cast<__FastTest *>(fastTest_ptr);
	return __fastTest_ref->portfolio.size();
}
void get_last_positions(void *fastTest_ptr, PositionArray *position_history) {
	__FastTest * __fastTest_ref = static_cast<__FastTest *>(fastTest_ptr);
	int number_positions = position_history->number_positions;

	if(position_history->number_positions != __fastTest_ref->portfolio.size()){
		throw std::runtime_error("incorrect position count passed to PositionArray object");
	}
	if(!__fastTest_ref->save_last_portfolio){
		throw std::runtime_error("last portfolio was not saved");
	}

	int i = 0;
	for (auto &kvp : __fastTest_ref->portfolio){
		PositionStruct &position_struct_ref = *position_history->POSITION_ARRAY[i];
		__fastTest_ref->portfolio[kvp.first].to_struct(position_struct_ref);
		i++;
	}
}
