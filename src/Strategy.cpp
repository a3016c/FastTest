#ifdef _WIN32
#include "pch.h"
#endif 
#include "Strategy.h"
#include "Exchange.h"
#include "Broker.h"
#include "Order.h"

Strategy::Strategy(__Exchange &exchangeObj, __Broker &brokerObj) :
	__exchange(exchangeObj), __broker(brokerObj)
{
}
void Strategy::next() {
}
void TestStrategy::register_test_map(std::vector<order_schedule>orders) {
	this->order_scheduler = orders;
}

void TestStrategy::next() {
	for (auto it = this->order_scheduler.begin(); it != this->order_scheduler.end();) {
		OrderResponse order_response;
		if (it->i == i) {
			switch (it->order_type) {
			case MARKET_ORDER: {
				this->__broker._place_market_order(&order_response, it->asset_id, it->units);
				break;
			}
			case LIMIT_ORDER: {
				this->__broker._place_limit_order(&order_response, it->asset_id, it->units, it->limit);
				break;
			}
			case STOP_LOSS_ORDER: {
				//Position* existing_position = &this->__broker.portfolio[it->asset_id];
				//this->__broker.place_stoploss_order(existing_position, &order_response, it->units, it->limit);
				break;
			}
			case TAKE_PROFIT_ORDER: {
				break;
			}
			}
			it = this->order_scheduler.erase(it);
		}
		else {
			it++;
		}
	}
	i++;
}