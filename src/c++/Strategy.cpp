#include "pch.h"
#include "Strategy.h"
#include "Exchange.h"
#include "Broker.h"
#include "Order.h"

Strategy::Strategy(Exchange &exchangeObj, Broker &brokerObj) :
	exchange(exchangeObj), broker(brokerObj)
{
}
std::vector<Order*> Strategy::next(){
	std::vector<Order*> new_orders;
	return new_orders;
}
std::vector<Order*> BenchmarkStrategy::next() {
	std::vector<Order*> new_orders;
	if (!this->is_invested) {
		std::string asset_name = "test1";
		Order* order = new MarketOrder(
			asset_name,
			this->broker.cash / this->exchange.get_market_price(asset_name, true),
			true
		);
		new_orders.push_back(order);
		this->is_invested = true;
	}
	return new_orders;
}
void TestStrategy::register_test_map(std::vector<order_schedule>orders) {
	this->orders = orders;
}

std::vector<Order*> TestStrategy::next() {
	std::vector<Order*> new_orders;
	for (auto it = this->orders.begin(); it != this->orders.end();) {
		if (it->i == i) {
			switch (it->order_type) {
			case MARKET_ORDER: {
				Order* order = new MarketOrder(it->asset_name, it->units);
				new_orders.push_back(order);
				it = this->orders.erase(it);
				break;
			}
			case LIMIT_ORDER: {
				Order* order = new LimitOrder(it->asset_name, it->units, it->limit);
				new_orders.push_back(order);
				it = this->orders.erase(it);
				break;
			}
			}
		}
		else {
			it++;
		}
	}
	i++;
	return new_orders;
}