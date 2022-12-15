#include "pch.h"
#include "Strategy.h"
#include "Exchange.h"
#include "Broker.h"
#include "Order.h"

Strategy::Strategy(Exchange &exchangeObj, Broker &brokerObj) :
	exchange(exchangeObj), broker(brokerObj)
{
}
std::vector<std::unique_ptr<Order>> Strategy::next(){
	std::vector<std::unique_ptr<Order>> new_orders;
	return new_orders;
}
std::vector<std::unique_ptr<Order>> BenchmarkStrategy::next() {
	std::vector<std::unique_ptr<Order>> new_orders;
	if (!this->is_invested) {
		std::string asset_name = "test1";
		std::unique_ptr<Order> order (new MarketOrder(
			asset_name,
			this->broker.cash / this->exchange.get_market_price(asset_name, true),
			true
		));
		new_orders.push_back(std::move(order));
		this->is_invested = true;
	}
	return new_orders;
}
void TestStrategy::register_test_map(std::vector<order_schedule>orders) {
	this->orders = orders;
}

std::vector<std::unique_ptr<Order>> TestStrategy::next() {
	std::vector<std::unique_ptr<Order>> new_orders;
	for (auto it = this->orders.begin(); it != this->orders.end();) {
		if (it->i == i) {
			switch (it->order_type) {
			case MARKET_ORDER: {
				std::unique_ptr<Order> order (new MarketOrder(it->asset_name, it->units));
				new_orders.push_back(std::move(order));
				it = this->orders.erase(it);
				break;
			}
			case LIMIT_ORDER: {
				std::unique_ptr<Order> order (new LimitOrder(it->asset_name, it->units, it->limit));
				new_orders.push_back(std::move(order));
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