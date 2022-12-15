#include "pch.h"
#include "Strategy.h"
#include "Exchange.h"
#include "Broker.h"
#include "Order.h"

Strategy::Strategy(Exchange &exchangeObj, Broker &brokerObj) :
	exchange(exchangeObj), broker(brokerObj)
{
}
void Strategy::next(){
}
void BenchmarkStrategy::next() {
	if (!this->is_invested) {
		std::string asset_name = "test1";
		this->broker.place_market_order(
			asset_name,
			this->broker.cash / this->exchange.get_market_price(asset_name, true),
			true
		);
		this->is_invested = true;
	}
}
void TestStrategy::register_test_map(std::vector<order_schedule>orders) {
	this->orders = orders;
}

void TestStrategy::next() {
	for (auto it = this->orders.begin(); it != this->orders.end();) {
		if (it->i == i) {
			switch (it->order_type) {
				case MARKET_ORDER: {
					this->broker.place_market_order(it->asset_name, it->units);
					break;
				}
				case LIMIT_ORDER: {
					this->broker.place_limit_order(it->asset_name, it->units, it->limit);
					break;
				}
			}
			it = this->orders.erase(it);
		}
		else {
			it++;
		}
	}
	i++;
}