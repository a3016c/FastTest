#include "pch.h"
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
void BenchmarkStrategy::next() {
	if (!this->is_invested) {
		std::string asset_name = "test1";
		this->__broker._place_market_order(
			asset_name,
			this->__broker.cash / this->__exchange._get_market_price(asset_name, true),
			true
		);
		this->is_invested = true;
	}
}
void TestStrategy::register_test_map(std::vector<order_schedule>orders) {
	this->order_scheduler = orders;
}

void TestStrategy::next() {
	for (auto it = this->order_scheduler.begin(); it != this->order_scheduler.end();) {
		if (it->i == i) {
			switch (it->order_type) {
			case MARKET_ORDER: {
				this->__broker._place_market_order(it->asset_name, it->units);
				break;
			}
			case LIMIT_ORDER: {
				this->__broker._place_limit_order(it->asset_name, it->units, it->limit);
				break;
			}
			case STOP_LOSS_ORDER: {
				Position* existing_position = &this->__broker.portfolio[it->asset_name];
				this->__broker.place_stoploss_order(existing_position, it->units, it->limit);
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